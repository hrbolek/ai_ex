import { useEffect, useState } from "react";
import { createClient } from 'graphql-ws';

export function useGraphQLSubscription({ query, variables, url, onData }) {
    const [data, setData] = useState();
    const [error, setError] = useState();

    useEffect(() => {
        const wsClient = createClient({ url });

        const onData_ = (result) => {
            setData(old => result.data)
            (onData && onData(result))
        }

        const unsubscribe = wsClient.subscribe(
        { query, variables },
        {
            next: onData_,
            error: setError,
            complete: () => {},
        }
        );
        return () => unsubscribe();
    }, [query, variables, url, onData]);

    return { data, error };
}

