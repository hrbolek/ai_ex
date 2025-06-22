import { useState, useEffect, useCallback, useRef } from "react";

export function useGraphQLQuery({ query, variables, url="/gql", deferred } = {}) {
    
    const [data, setData] = useState();
    const [error, setError] = useState();
    const [loading, setLoading] = useState(false);
    // Uložíme poslední proměnné kvůli možnost fetch s novými
    const lastVars = useRef(variables);

    const fetch = useCallback(async (vars = lastVars.current) => {
        setLoading(true);
        setError(undefined);
        try {
            const res = await fetchGraphQL(url, query, vars);
            setData(res.data);
            setLoading(false);
            lastVars.current = vars;
            return res;
        } catch (e) {
            setError(e);
            setLoading(false);
        }
    }, [url, query]);

    useEffect(() => {
        if (!deferred) {
            fetch(variables);
        }
        // eslint-disable-next-line
    }, [query, JSON.stringify(variables), url, deferred]);

    return { data, error, loading, fetch };
}

async function fetchGraphQL(url, query, variables) {
    const res = await fetch(url, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
        },
        body: JSON.stringify({ query, variables })
    });
    const result = await res.json();
    if (result.errors) throw result.errors;
    return result;
}
