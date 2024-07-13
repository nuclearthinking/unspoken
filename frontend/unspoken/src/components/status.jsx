import React, {memo} from "react";
import {Chip, Spinner} from "@nextui-org/react";
import "../index.css";

function StatusChip(props) {
    const {status, key} = props;

    const statusMap = {
        completed: {color: "success"},
        failed: {color: "danger"},
        queued: {color: "default"},
        conversion: {
            color: "secondary",
            endContent: <Spinner color="secondary" size="sm"/>,
        },
        diarization: {
            color: "secondary",
            endContent: <Spinner color="secondary" size="sm"/>,
        },
        transcribing: {
            color: "secondary",
            endContent: <Spinner color="secondary" size="sm"/>,
        },
        default: {color: "default"},
    };

    const {color, endContent} = statusMap[status] || statusMap.default;

    return (
        <Chip color={color} key={key} variant="flat" endContent={endContent}>
            {status}
        </Chip>
    );
}

export default memo(StatusChip);
