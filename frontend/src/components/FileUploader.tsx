import { useRef } from 'react'

const VALID_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
const MAX_SIZE_BYTES = 10 * 1024 * 1024

export interface FileUploaderProps {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

const FileUploader = ({ onFileSelected, disabled }: FileUploaderProps) => {
  const inputRef = useRef<HTMLInputElement | null>(null)

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!VALID_TYPES.includes(file.type)) {
      alert('Please choose a JPG, PNG, or PDF file.')
      event.target.value = ''
      return
    }

    if (file.size > MAX_SIZE_BYTES) {
      alert('File size must be under 10MB.')
      event.target.value = ''
      return
    }

    onFileSelected(file)
    event.target.value = ''
  }

  const triggerFileSelect = () => {
    if (disabled) return
    inputRef.current?.click()
  }

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,application/pdf"
        onChange={handleChange}
        className="hidden"
        aria-hidden="true"
        tabIndex={-1}
      />
      <button
        type="button"
        onClick={triggerFileSelect}
        disabled={disabled}
        className={`
          inline-flex h-11 w-11 items-center justify-center rounded-lg
          border border-aqua text-aqua bg-transparent
          transition-all duration-200 ease-in-out
          hover:bg-aqua-hover
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-aqua
          ${disabled ? 'opacity-50 pointer-events-none' : ''}
        `}
        aria-label="Upload file"
      >
        <span className="text-base">📎</span>
      </button>
    </>
  )
}

export default FileUploader
