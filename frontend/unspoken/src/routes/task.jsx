import React, {useEffect, useState} from "react";
import {
    Link,
    useLoaderData,
    useNavigation,
    useParams,
} from "react-router-dom";
import {Chip, Spacer, Spinner} from "@nextui-org/react";
import StatusChip from "../components/status";
import Message from "../components/message";
import "../index.css";
import {getBackendUrl} from "../common";

function Tasks() {
    const {id} = useParams();
    const {data} = useLoaderData();
    const {state} = useNavigation();
    const [task, setTask] = useState(data);

    function isFinal(task) {
        return task.status === "completed" || task.status === "failed";
    }

    useEffect(() => {
        const fetchData = async (id) => {
            const response = await fetch(
                `${getBackendUrl()}/task/${id}/`
            );
            return await response.json();
        };
        let interval;
        if (!isFinal(task)) {
            interval = setInterval(async () => {
                const fetchedData = await fetchData(id);
                setTask(fetchedData);
                if (isFinal(fetchedData)) {
                    clearInterval(interval);
                }
            }, 5000);

            return () => clearInterval(interval);
        }
    }, [id, task]);

    if (state === "loading") {
        return <Spinner color="secondary" size="lg"/>;
    }

    return (
        <div>
            <div className="flex justify-start">
                <div className="mr-2">
                    <Link to={`/`}>
                        <img src="/home.svg" style={{width: 25}}/>
                    </Link>
                </div>
                <div className="mr-2">
                    <Chip radius="sm">id: {task.id}</Chip>
                </div>
                <div className="mr-2">
                    <StatusChip status={task.status}/>
                </div>
                <div className="mr-2">
                    <p className="font-mono line-clamp-1">{task?.file_name}</p>
                </div>
            </div>
            <Spacer y={3}/>

            {task.status === "completed" && (
                <div>
                    {task.messages.map((message, i) => (
                        <Message key={i} text={message.text} speaker={message.speaker} start={message.start}/>
                    ))}
                </div>
            )}
        </div>
    );
}

export default Tasks;
