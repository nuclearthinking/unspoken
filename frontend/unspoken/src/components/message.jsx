import { Card, CardBody, CardHeader } from "@nextui-org/react";

export default function Message(props) {
  const { speaker, text } = props;

  const speakerStyles = {
    speaker_0: "message-violet",
    speaker_1: "message-blue",
    speaker_2: "message-indigo",
    speaker_3: "message-purple",
    speaker_4: "message-pink",
    unknown: "message-rose",
  };

  const messageStyle = speakerStyles[speaker] || speakerStyles.unknown;

  return (
    <Card className={`message flat ${messageStyle}`} variant="flat">
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
