import React from "react";
import { Chip, Spinner } from "@nextui-org/react";
import "../index.css";

export default function StatusChip(props) {
  const { status } = props;

  var color = "";
  var endContent = "";
  
  switch (status) {
    case "completed":
      color = "success";
      break;
    case "failed":
      color = "danger";
      break;
    case "queued":
      color = "default";
      
      break;
    case "processing":
      color = "secondary";
      endContent = <Spinner color="secondary" size="sm" />;
      break;
    default:
      color = "default";
  }

  return (
    <Chip color={color} variant="flat" endContent={endContent}>
      {status}
    </Chip>
  );
}
