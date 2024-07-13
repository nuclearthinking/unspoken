import {user} from "@nextui-org/react";
import {useRouteError} from "react-router-dom";

export default function ErrorPage() {
    const {error} = useRouteError();
    return (
        <div id="error-page">
            <h1>Oops!</h1>
            <p>Sorry, an unexpected error has occurred.</p>
            <p>
                <i>Error :(</i>
            </p>
        </div>
    );
}