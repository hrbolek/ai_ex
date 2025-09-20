import { useEffect, useState, useRef } from "react";
import { createClient } from 'graphql-ws';

export function useGraphQLSubscription({ url, query, variables, onData }) {
  const [error, setError] = useState(null);
  const onDataRef = useRef(onData);
  const varsRef = useRef(variables);
  const queryRef = useRef(query);

  // keep refs up to date
  useEffect(() => {
    onDataRef.current = onData;
  }, [onData]);

  useEffect(() => {
    queryRef.current = query;
  }, [query]);

  useEffect(() => {
    varsRef.current = variables;
  }, [variables]);

  useEffect(() => {
    const wsClient = createClient({ url });
    const unsubscribe = wsClient.subscribe(
      () => ({
        query: queryRef.current,
        variables: varsRef.current,
      }),
      {
        next: result => {
          try {
            onDataRef.current(result);
          } catch (e) {
            console.error("Error in onData handler", e);
          }
        },
        error: err => {
          console.error("WSSubscription error", err);
          setError(err);
        },
        complete: () => {
          // completed
        },
      }
    );

    return () => {
      unsubscribe();
      wsClient.dispose();
    };
  }, [url]);

  return { error };
}
