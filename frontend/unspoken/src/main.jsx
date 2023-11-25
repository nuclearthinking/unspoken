import React from "react";
import ReactDOM from "react-dom/client";
import Root from "./routes/root.jsx";
import Tasks from "./routes/task.jsx";
import "./index.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ErrorPage from "./error-page.jsx";
import { NextUIProvider } from "@nextui-org/react";

const fetchData = async (id) => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/task/${id}/`);
  const data = await response.json();
  return data;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/tasks/:id",
    loader: async ({ params }) => {
      const data = await fetchData(params.id);
      return {data}
    },
    element: <Tasks />,
    errorElement: <ErrorPage />,
    
  },
  {
    path: "/404",
    element: <ErrorPage />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <NextUIProvider>
      <RouterProvider router={router} />
    </NextUIProvider>
  </React.StrictMode>
);
