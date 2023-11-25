import React, { useState, useEffect } from "react";
import {
  useParams,
  useNavigate,
  useLoaderData,
  useNavigation,
} from "react-router-dom";
import { Chip, Spacer, Spinner } from "@nextui-org/react";
import StatusChip from "../components/status";
import Message from "../components/message";
import "../index.css";

function Tasks(props) {
  const { id } = useParams();
  const loadedData = useLoaderData();
  const { data } = loadedData;
  const { state } = useNavigation();

  useEffect(() => {
    console.log(loadedData);
  }, [id]);

  if (state === "loading") {
    return <Spinner color="secondary" size="lg" />;
  }

  if (data?.status !== "completed") {
    console.log("data:", data);
    return (
      <div className="flex flex-row">
        <div className="basis-1/6">
          <Chip radius="sm">id: {data?.id}</Chip>
        </div>
        <div className="basis-1/6">
          <StatusChip status={data?.status} />
        </div>
        <div className="basis-2/3">
          <p className="font-mono line-clamp-1">{data?.file_name}</p>
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
        <div className="basis-2/3">
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
