import { Card, CardBody, CardHeader } from "@nextui-org/react";

export default function Message(props) {
  const { speaker, text } = props;

  var messageStyle = "";

  switch (speaker) {
    case "speaker_0":
      messageStyle = "message-violet";
      break;
    case "speaker_1":
      messageStyle = "message-blue";
      break;
    case "speaker_2":
      messageStyle = "message-indigo";
      break;
    case "speaker_3":
      messageStyle = "message-purple";
      break;
    case "speaker_4":
      messageStyle = "message-pink";
      break;
    case "unknown":
      messageStyle = "message-rose";
      break;
    default:
      messageStyle = "message-blue";
  }

  return (
    <Card className={`message flat ` + messageStyle} variant="flat">
      <CardHeader className="justify-between" variant="flat">
        <div className="flex gap-4">
          <div className="flex  items-start justify-center uncopy">
            <h5 className="text-small tracking-tight text-default-400">
              @{speaker}
            </h5>
          </div>
        </div>
      </CardHeader>
      <CardBody variant="flat">
        <p className="font-mono">
          <span className="hidden-text">{speaker}: </span>
          {text}
        </p>
      </CardBody>
    </Card>
  );
}
