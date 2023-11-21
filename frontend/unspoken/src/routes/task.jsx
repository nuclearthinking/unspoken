import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Card, CardHeader, CardBody, CardFooter } from "@nextui-org/react";
import '../index.css'

function Tasks() {
  const [data, setData] = useState(null);
  const { id } = useParams();
  useEffect(() => {
    fetch(`http://0.0.0.0:8000/task/${id}`)
      .then((response) => response.json())
      .then((data) => setData(data));
  }, [id]);

  if (data === null) {
    return <div>Loading...</div>;
  }

  if (data.status != "completed") {
    return (
      <div>
        <h1>Task id: {data.id}</h1>
        <h2>Status: {data.status}</h2>

        <p>File name: {data.file_name}</p>
      </div>
    );
  }
  console.log(data);
  return (
    <div>
      <h1 className="text-xl font-bold">Task id: {data.id}</h1>
      <h2>Status: {data.status}</h2>

      <p>File name: {data.file_name}</p>

      <div>
        {data.messages.map((message, i) => (
          <Card key={i}>
            <CardBody>
              <p>
                {message.speaker}: {message.text}
              </p>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default Tasks;
