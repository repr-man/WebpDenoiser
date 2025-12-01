import struct


class VP8Tool:
    def __init__(self, rawWebp: bytes):
        if len(rawWebp) < 8:
            raise ValueError("Invalid WebP file: too short")

        assert rawWebp[0:4] == b'RIFF', "File does not start with RIFF header"
        try:
            riffSize: int = struct.unpack('<I', rawWebp[4:8])[0]
        except:
            raise ValueError("Invalid RIFF size")
        
        assert rawWebp[8:12] == b'WEBP', "Invalid RIFF form-type signature"
        assert rawWebp[12:16] == b'VP8 ', "Did not find VP8 chunk signature"
        try:
            vp8Size: int = struct.unpack('<I', rawWebp[16:20])[0]
        except:
            raise ValueError("Invalid VP8 chunk size")
        vp8End = 20 + vp8Size
        assert vp8End <= len(rawWebp), "VP8 chunk size is too large"
        
        self.raw = rawWebp[20:vp8End]

    def decode(self):
        decoder = VP8Decoder(self.raw)
        return decoder.decode()


class BooleanDecoder:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
        self.value = 0
        self.range = 255
        self.bit_count = 0
        
        # Initialize
        self.value = (self.data[0] << 8) | self.data[1]
        self.offset = 2
        self.bit_count = 0

    def read_bit(self, prob: int) -> int:
        split = (self.range * prob) >> 8
        bit = 0
        if self.value >= (split << 8):
            bit = 1
            self.value -= (split << 8)
            self.range -= split
        else:
            bit = 0
            self.range = split
            
        while self.range < 128:
            self.value <<= 1
            self.range <<= 1
            self.bit_count += 1
            if self.bit_count == 8:
                self.bit_count = 0
                if self.offset < len(self.data):
                    self.value |= self.data[self.offset]
                    self.offset += 1
                    
        return bit

    def read_bool(self) -> int:
        split = self.range >> 1
        bit = 0
        if self.value >= (split << 8):
            bit = 1
            self.value -= (split << 8)
            self.range -= split
        else:
            bit = 0
            self.range = split
            
        while self.range < 128:
            self.value <<= 1
            self.range <<= 1
            self.bit_count += 1
            if self.bit_count == 8:
                self.bit_count = 0
                if self.offset < len(self.data):
                    self.value |= self.data[self.offset]
                    self.offset += 1
                    
        return bit

    def read_value(self, bits: int) -> int:
        v = 0
        for _ in range(bits):
            v = (v << 1) | self.read_bool()
        return v
    
    def read_literal(self, bits: int) -> int:
        v = 0
        for _ in range(bits):
            v = (v << 1) | self.read_bool()
        return v


def clamp(val):
    if val < 0: return 0
    if val > 255: return 255
    return int(val)

class VP8Decoder:
    def __init__(self, data: bytes):
        self.data = data
        self.bd = None
        self.width = 0
        self.height = 0
        self.y_stride = 0
        self.uv_stride = 0
        self.y_data = None
        self.u_data = None
        self.v_data = None
        
    def decode(self):
        # Frame Header
        # 1-bit frame type (0 = keyframe, 1 = interframe)
        # 3-bit version number
        # 1-bit show_frame
        # 19-bit first partition size
        
        # We need to read the first 3 bytes uncompressed
        b0 = self.data[0]
        b1 = self.data[1]
        b2 = self.data[2]
        
        frame_type = (b0 & 1)
        #version = (b0 >> 1) & 7
        #show_frame = (b0 >> 4) & 1
        #first_part_size = (b0 >> 5) | (b1 << 3) | (b2 << 11)
        
        if frame_type != 0:
            raise ValueError("Interframes not supported")
            
        # Keyframe header
        # 3 bytes start code: 0x9d 0x01 0x2a
        if self.data[3] != 0x9d or self.data[4] != 0x01 or self.data[5] != 0x2a:
            raise ValueError("Invalid start code")
            
        # 16 bits: (2 bits scale, 14 bits width)
        # 16 bits: (2 bits scale, 14 bits height)
        w_raw = struct.unpack('<H', self.data[6:8])[0]
        h_raw = struct.unpack('<H', self.data[8:10])[0]
        
        self.width = w_raw & 0b11111111111111
        self.height = h_raw & 0b11111111111111
        
        # Initialize Boolean Decoder with the rest of the data
        # The first partition starts at offset 10
        self.bd = BooleanDecoder(self.data[10:])
        
        # Parse Frame Header details (RFC 6386 Section 9.2)
        
        # Color space (1 bit)
        if self.bd.read_bool():
            # 1 = YUV color space (standard for WebP)
            pass 
        else:
             # 0 = YCgCo color space (not typically used in WebP)
            pass
            
        # Clamping type (1 bit)
        self.bd.read_bool() 
        
        # Segmentation (Section 9.3)
        segmentation_enabled = self.bd.read_bool()
        if segmentation_enabled:
            update_mb_segmentation_map = self.bd.read_bool()
            update_segment_feature_data = self.bd.read_bool()
            
            if update_segment_feature_data:
                # Read segment feature data
                # 4 segments
                for i in range(4):
                    # Segment feature mode (0 = delta, 1 = absolute)
                    self.bd.read_bool()
                    # Quantizer update
                    if self.bd.read_bool():
                        self.bd.read_value(7)
                        self.bd.read_bool() # Sign
                    # Loop filter update
                    if self.bd.read_bool():
                        self.bd.read_value(6)
                        self.bd.read_bool() # Sign

            if update_mb_segmentation_map:
                # Read segment probs (3 probs)
                for i in range(3):
                    if self.bd.read_bool():
                        self.bd.read_value(8)
                        
        # Filter Type (1 bit)
        self.bd.read_bool()
        
        # Loop Filter Level (6 bits)
        self.bd.read_literal(6)
        
        # Sharpness Level (3 bits)
        self.bd.read_literal(3)
        
        # Mode Ref LF Delta (Section 9.4)
        if self.bd.read_bool(): # mode_ref_lf_delta_enabled
            if self.bd.read_bool(): # mode_ref_lf_delta_update
                # 4 ref deltas
                for i in range(4):
                    if self.bd.read_bool():
                        self.bd.read_literal(6)
                        self.bd.read_bool() # Sign
                # 4 mode deltas
                for i in range(4):
                    if self.bd.read_bool():
                        self.bd.read_literal(6)
                        self.bd.read_bool() # Sign
                        
        # Log2 Nbr of DCT Partitions (2 bits)
        self.bd.read_literal(2)
        
        # Quantization Indices (Section 9.6)
        # y1_ac_qi (7 bits)
        self.bd.read_literal(7)
        
        # y1_dc_delta_present (1 bit)
        if self.bd.read_bool():
            self.bd.read_literal(4)
            self.bd.read_bool() # Sign
            
        # y2_dc_delta_present (1 bit)
        if self.bd.read_bool():
            self.bd.read_literal(4)
            self.bd.read_bool() # Sign
            
        # y2_ac_delta_present (1 bit)
        if self.bd.read_bool():
            self.bd.read_literal(4)
            self.bd.read_bool() # Sign
            
        # uv_dc_delta_present (1 bit)
        if self.bd.read_bool():
            self.bd.read_literal(4)
            self.bd.read_bool() # Sign
            
        # uv_ac_delta_present (1 bit)
        if self.bd.read_bool():
            self.bd.read_literal(4)
            self.bd.read_bool() # Sign
            
        # Refresh Entropy Probs (1 bit) - Keyframe doesn't have this in the same way, 
        # but RFC 9.2 implies it might be read. 
        # Actually for Key Frames, "refresh_entropy_probs" is not read. 
        # But "Token Probabilities" (Section 9.9) are loaded with defaults.
        # However, Section 9.10 says "The probability update data...".
        # For Key Frames, we might need to skip this check or it's implicitly 0.
        # Wait, RFC says: "If the frame is a Key Frame... the following bits are read... (list ends at Quantization Indices)".
        # Then "Token Probabilities" section says: "If the frame is a Key Frame, the default probabilities are loaded...".
        # But then Section 9.10 "Token Probabilities" says: "The probability update data is stored...".
        # Let's check libwebp or another reference. 
        # In libwebp, for keyframes, it parses color space, clamp, segmentation, filter, partitions, quant.
        # Then it parses mb_no_coeff_skip (1 bit).
        # Then it parses prob updates.
        
        # mb_no_coeff_skip (1 bit)
        self.bd.read_bool()
        
        # Token Probabilities (Section 9.10)
        # For each of the 4 types, 8 bands, 3 nodes, 11 probs
        for i in range(4):
            for j in range(8):
                for k in range(3):
                    for l in range(11):
                        if self.bd.read_bool(): # coeff_prob_update_flag
                            self.bd.read_literal(8) # prob_update_value
        
        # Initialize buffers
        self.y_stride = self.width
        self.uv_stride = self.width // 2
        self.y_data = [0] * (self.y_stride * self.height)
        self.u_data = [0] * (self.uv_stride * (self.height // 2))
        self.v_data = [0] * (self.uv_stride * (self.height // 2))
        
        # Decode macroblocks (Simplified: just filling with grey for now to test structure)
        # Real implementation requires parsing probabilities, modes, coeffs, etc.
        
        return self.yuv_to_rgb()

    def yuv_to_rgb(self):
        # Basic YUV to RGB conversion
        rgb = bytearray(self.width * self.height * 3)
        for y in range(self.height):
            for x in range(self.width):
                Y = self.y_data[y * self.y_stride + x]
                U = self.u_data[(y // 2) * self.uv_stride + (x // 2)]
                V = self.v_data[(y // 2) * self.uv_stride + (x // 2)]
                
                C = Y - 16
                D = U - 128
                E = V - 128
                
                R = clamp((298 * C + 409 * E + 128) >> 8)
                G = clamp((298 * C - 100 * D - 208 * E + 128) >> 8)
                B = clamp((298 * C + 516 * D + 128) >> 8)
                
                idx = (y * self.width + x) * 3
                rgb[idx] = R
                rgb[idx+1] = G
                rgb[idx+2] = B
        return bytes(rgb)
