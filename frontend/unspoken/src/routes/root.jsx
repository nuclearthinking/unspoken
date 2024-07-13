import React, {useRef} from "react";
import {DndProvider, useDrop} from "react-dnd";
import {HTML5Backend, NativeTypes} from "react-dnd-html5-backend";
import {
    Uploady,
    useUploady,
    useItemProgressListener,
    useItemFinishListener,
} from "@rpldy/uploady";
import {Line} from "rc-progress";
import {useNavigate} from "react-router-dom";
import "../index.css";
import {getBackendUrl} from "../common";

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
            {entries.map(([id, {progress, name}]) => {
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
    const {upload} = useUploady();
    const fileInputRef = useRef();

    const handleInputChange = (e) => {
        upload(e.target.files);
    };

    const [{isDragging}, dropRef] = useDrop({
        accept: NativeTypes.FILE,
        collect: (monitor) => ({
            isDragging: !!monitor.isOver(),
        }),
        drop: (item) => {
            upload(item.files);
        },
    });

    const openFileInput = () => {
        fileInputRef.current.click();
    };

    return (
        <div
            ref={dropRef}
            className={isDragging ? "drop-zone-hover" : "drop-zone"}
            style={{
                width: "35vw",
                height: "30vh",
            }}
            onClick={openFileInput}
        >
            <input
                type="file"
                style={{display: "none"}}
                ref={fileInputRef}
                onChange={handleInputChange}
            />
            <p/>
            <p className="font-mono text-white text-lg">Upload file</p>
        </div>
    );
};


function Root() {
    return (
        <DndProvider backend={HTML5Backend}>
            <Uploady
                destination={{url: getBackendUrl() + "/upload/media"}}
            >
                <DropZone/>
                <UploadProgress/>
            </Uploady>
        </DndProvider>
    );
}

export default Root;
