import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload } from 'lucide-react'
import { API } from '@/api'
import { useNavigate } from 'react-router-dom'

export default function Home() {
    const [uploading, setUploading] = useState(false)
    const [uploadError, setUploadError] = useState<string | null>(null)
    const [uploadSuccess, setUploadSuccess] = useState(false)
    const navigate = useNavigate()

    const handleUpload = useCallback(async (file: File) => {
        setUploading(true)
        setUploadError(null)
        setUploadSuccess(false)

        try {
            const formData = new FormData()
            formData.append('file', file)

            const response = await fetch(API.upload, {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Upload failed')
            }

            const data = await response.json()
            setUploadSuccess(true)
            navigate(`/task/${data.task_id}`)
        } catch (error) {
            setUploadError('Failed to upload file. Please try again.')
            console.error('Upload error:', error)
        } finally {
            setUploading(false)
        }
    }, [navigate])

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles && acceptedFiles.length > 0) {
            handleUpload(acceptedFiles[0])
        }
    }, [handleUpload])

    const { getRootProps, getInputProps, isDragActive, fileRejections, open } = useDropzone({
        onDrop,
        accept: {
            'audio/*': [],
            'video/*': []
        },
        maxFiles: 1,
        multiple: false,
        noClick: true,
    })

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-24">
            <h1 className="text-4xl font-bold mb-8 text-gray-800">UNSPOKEN</h1>
            <div
                {...getRootProps()}
                className={`w-full max-w-2xl p-12 text-center border-4 border-dashed rounded-lg transition-colors h-64 flex flex-col items-center justify-center ${isDragActive ? 'border-blue-400 bg-blue-100' : 'border-gray-300 bg-white'
                    }`}
            >
                <input {...getInputProps()} />
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-4 text-lg text-gray-600">
                    {isDragActive
                        ? 'Drop the file here...'
                        : uploading
                            ? 'Uploading...'
                            : 'Drag & drop audio or video file here'}
                </p>
                <button
                    onClick={open}
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                    disabled={uploading}
                >
                    Select File
                </button>
            </div>
            {uploadError && (
                <p className="mt-4 text-sm text-red-500">{uploadError}</p>
            )}
            {uploadSuccess && (
                <p className="mt-4 text-sm text-green-500">File uploaded successfully!</p>
            )}
            {fileRejections.length > 0 && (
                <div className="mt-4 text-red-500">
                    {fileRejections.map(({ file, errors }) => (
                        <p key={file.name}>
                            {file.name} - {errors.map(e => e.message).join(', ')}
                        </p>
                    ))}
                </div>
            )}
        </div>
    )
}