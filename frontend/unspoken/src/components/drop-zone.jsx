import React from "react";
import { DndProvider, useDrop } from "react-dnd";
import Backend, { NativeTypes } from "react-dnd-html5-backend";
import Uploady, { useUploady } from "@rpldy/uploady";

const DropZone = () => {
   const { upload } = useUploady();
   const [{ isDragging }, dropRef] = useDrop({
       accept: NativeTypes.FILE,
       collect: ((monitor) => ({
           isDragging: !!monitor.isOver()
       })),
       drop: (item) => { 					 					
           upload(item.files);						
       },
   });
   return <div ref={dropRef} className={isDragging ? "drag-over" : ""}>      
       <p>Drop File(s) Here</p>      
   </div>;
};

export default DropZone;