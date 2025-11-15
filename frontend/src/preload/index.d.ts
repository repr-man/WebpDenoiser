import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI & {
      selectDirectory: (options?: Electron.OpenDialogOptions) => Promise<string>
    }
    api: unknown
  }
}
