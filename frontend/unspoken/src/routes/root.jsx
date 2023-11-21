import React from "react";
import { DndProvider, useDrop } from "react-dnd";
import { HTML5Backend, NativeTypes } from "react-dnd-html5-backend";
import {
  Uploady,
  useUploady,
  useItemProgressListener,
  useItemFinishListener,
} from "@rpldy/uploady";
import { Line } from "rc-progress";
import { useNavigate } from "react-router-dom";


const UploadProgress = () => {
  const [uploads, setUploads] = React.useState({});
  
  const progressData = useItemProgressListener();
  
  const navigate = useNavigate();
  useItemFinishListener((item) => {
    console.log(item);
    if ((item.state == "finished") & (item.uploadStatus == 200)) {
      navigate(`/tasks/${item.uploadResponse.data.task_id}`);
    }
  });

  if (progressData && progressData.completed) {
    const upload = uploads[progressData.id] || {
      name: progressData.url || progressData.file.name,
      progress: [0],
    };

    if (!~upload.progress.indexOf(progressData.completed)) {
      upload.progress.push(progressData.completed);

      setUploads({
        ...uploads,
        [progressData.id]: upload,
      });
    }
  }

  const entries = Object.entries(uploads);

  return (
    <div>
      {entries.map(([id, { progress, name }]) => {
        const lastProgress = progress[progress.length - 1];

        return (
          <div key={id}>
            <Line
              strokeWidth={2}
              strokeColor={lastProgress === 100 ? "#00a626" : "#2db7f5"}
              percent={lastProgress}
            />
          </div>
        );
      })}
    </div>
  );
};

const DropZone = () => {
  const { upload } = useUploady();

  const [{ isDragging }, dropRef] = useDrop({
    accept: NativeTypes.FILE,
    collect: (monitor) => ({
      isDragging: !!monitor.isOver(),
    }),
    drop: (item) => {
      upload(item.files);
    },
  });

  return (
    <div
      ref={dropRef}
      className={isDragging ? "drag-over" : ""}
      style={{
        border: "2px solid black",
        width: "35vw",
        height: "30vh",
      }}
    >
      <p>Drop File(s) Here</p>
    </div>
  );
};

function Root() {
  return (
    <DndProvider backend={HTML5Backend}>
      <Uploady destination={{ url: "http://0.0.0.0:8000/upload/audio" }}>
        <DropZone />
        <UploadProgress />
      </Uploady>
    </DndProvider>
  );
}

export default Root;
