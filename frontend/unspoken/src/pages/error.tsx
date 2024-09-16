import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"

export default function ErrorPage() {

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <header className="sticky top-0 z-10 w-full border-b bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex-1 flex justify-center sm:justify-start">
              <div className="flex items-center space-x-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-6 w-6"
                >
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" x2="12" y1="19" y2="22" />
                </svg>
                <span className="font-bold text-xl">UNSPOKEN</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      <main className="flex-1 flex items-center justify-center py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 text-center">
          <div>
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Oops! Something went wrong</h2>
            <p className="mt-2 text-sm text-gray-600">
              We couldn't find the page you're looking for. You can use the button below to return to the home page.
            </p>
          </div>
          <div className="mt-8">
          <Button asChild className="w-full">
            <Link to="/">Go back home</Link>
          </Button>
        </div>
        </div>
      </main>
    </div>
  )
}