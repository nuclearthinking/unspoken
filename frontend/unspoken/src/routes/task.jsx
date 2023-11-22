import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Chip,
  Spacer,
} from "@nextui-org/react";
import StatusChip from "../components/status";
import Message from "../components/message";
import "../index.css";

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
      <div className="flex flex-row">
        <div className="basis-1/6">
          <Chip radius="sm">id: {data.id}</Chip>
        </div>
        <div className="basis-1/6">
          <StatusChip status={data.status} />
        </div>
        <div className="basis-2/3">
          <p className="font-mono line-clamp-1">{data.file_name}</p>
        </div>
      </div>
    );
  }
  return (
    <div>
      <div className="flex flex-row">
        <div className="basis-1/6">
          <Chip radius="sm">id: {data.id}</Chip>
        </div>
        <div className="basis-1/6">
          <StatusChip status={data.status} />
        </div>
        <div classname="basis-2/3">
          <p className="font-mono line-clamp-1">{data.file_name}</p>
        </div>
      </div>
      <Spacer y={3} />

      <div>
        {data.messages.map((message, i) => (
          <Message key={i} text={message.text} speaker={message.speaker} />
        ))}
      </div>
    </div>
  );
}

export default Tasks;
