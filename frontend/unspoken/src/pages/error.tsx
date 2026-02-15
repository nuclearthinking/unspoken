import { Button } from "@/components/ui/button"
import { Link, useRouteError, isRouteErrorResponse } from "react-router-dom"
import { FileQuestion, ServerCrash, AlertTriangle } from "lucide-react"

function getErrorContent(error: unknown) {
  if (isRouteErrorResponse(error)) {
    if (error.status === 404) {
      return {
        code: "404",
        icon: <FileQuestion className="h-16 w-16 text-muted-foreground/60" />,
        title: "Task not found",
        description:
          "This task doesn't exist or has been deleted. It may have been removed by its owner.",
      }
    }

    if (error.status === 400) {
      return {
        code: "400",
        icon: <AlertTriangle className="h-16 w-16 text-amber-500/60" />,
        title: "Bad request",
        description:
          "The request was invalid. Please check the URL and try again.",
      }
    }

    return {
      code: String(error.status),
      icon: <ServerCrash className="h-16 w-16 text-destructive/60" />,
      title: "Something went wrong",
      description:
        "An unexpected server error occurred. Please try again later.",
    }
  }

  return {
    code: "500",
    icon: <ServerCrash className="h-16 w-16 text-destructive/60" />,
    title: "Something went wrong",
    description:
      "An unexpected error occurred while loading this page. Please try again later.",
  }
}

export default function ErrorPage() {
  const error = useRouteError()
  const { code, icon, title, description } = getErrorContent(error)

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <header className="sticky top-0 z-10 w-full border-b bg-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex-1 flex justify-center sm:justify-start">
              <Link to="/" className="flex items-center space-x-2">
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
              </Link>
            </div>
          </div>
        </div>
      </header>
      <main className="flex-1 flex items-center justify-center py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 text-center">
          <div className="flex flex-col items-center space-y-4">
            {icon}
            <p className="text-7xl font-bold text-muted-foreground/30">{code}</p>
          </div>
          <div>
            <h2 className="text-3xl font-extrabold">{title}</h2>
            <p className="mt-3 text-muted-foreground">{description}</p>
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
