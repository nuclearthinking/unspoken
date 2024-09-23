import { createBrowserRouter,  RouterProvider , LoaderFunctionArgs} from 'react-router-dom'
import Upload from '@/pages/upload'
import Task, { loader as taskLoader } from '@/pages/task'
import LabelingList, { loader as labelingLoader } from '@/pages/labeling'
import ErrorPage from '@/pages/error'
import { TaskResponse, LabelingTaskResponse } from '@/types/api'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Upload />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/task/:taskId",
    element: <Task />,
    loader: taskLoader as (args: LoaderFunctionArgs) => Promise<TaskResponse>,
    errorElement: <ErrorPage />,
  },
  {
    path: "/labeling/:taskId",
    element: <LabelingList />,
    loader: labelingLoader as (args: LoaderFunctionArgs) => Promise<LabelingTaskResponse>,
    errorElement: <ErrorPage />,
  },
]);

function App() {
  return <RouterProvider router={router} />
}

export default App
