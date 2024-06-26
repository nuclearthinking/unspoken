import { Card, CardBody, CardHeader } from "@nextui-org/react";

export default function Message(props) {
  const { speaker, text, start } = props;

  const toTimeStamp = (time) => {
    var date = new Date(0);
    date.setSeconds(Math.trunc(time));
    return date.toISOString().substring(11, 19);
  };


  return (
    <div className="flex justify-start">
      <div>
        <Card className="message flat" variant="flat">
          <CardHeader className="justify-between" variant="flat">
            <div className="flex gap-4">
              <div className="flex  items-start justify-center uncopy">
                <h5 className="text-small tracking-tight text-default-400">
                  {start ? toTimeStamp(start) : '00:00:00'}
                </h5>
              </div>
              <div className="flex  items-start justify-center uncopy">
                <h5 className="text-small tracking-tight text-default-400">
                  @{speaker}
                </h5>
              </div>
            </div>
          </CardHeader>
          <CardBody variant="flat">
            <p className="font-mono">
              <span className="hidden-text">{start ? toTimeStamp(start) : '00:00:00'} - {speaker}: </span>
              {text}
            </p>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}