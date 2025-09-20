import { useState, useCallback, useMemo } from 'react';
import { AutoGrowTextarea } from './AutoGrowTextarea';
import { HistoryItem } from './HistoryItem';
import { Loader } from './Loader';
import { useGraphQLSubscription } from '../useGraphQLSubscription';
import { useGraphQLQuery } from '../useGraphQLQuery';

export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const subscriptionQuery = `subscription Sub {
  result: userChannelMessages(channel: "ba05ce5d-5bbe-4847-bc44-d4b4b2c94771") {
    __typename
    msg
    attachments {
      __typename
      ... on DocumentFragmentGQLModel {
        url
      }
    }
  }
}`;

const searchQuery = `query search($search: String!) {
  searchByText(search: {query: $search}) {
    documentFragments {
      url
    }
    documents {
      url
    }
  }
}`

const apiQuery = `query search($search: String!) {
  apiQueryByText(apiCall: {query: $search, id: "ba05ce5d-5bbe-4847-bc44-d4b4b2c94771"})
}`

export const SearchDoc = () => {
    const [search, setSearch] = useState("");
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    const { 
        data: query_response, 
        error: query_error, 
        loading: query_loading, 
        fetch 
    } = useGraphQLQuery({
        // query: searchQuery, 
        query: apiQuery,
        variables: {"search": ""}, 
        deferred: true
    })

    const addHistory = (newItem) => {
        setHistory(
            items => {
                const item = newItem || { "type": "userPrompt", "text": search, "id": crypto.randomUUID() };
                setSearch(search => "");
                return [...items, item];
            }
        );
    };

    const onChange = (e) => {
        const value = e.target.value;
        setSearch(search => value);
    };

    const onSend = async () => {
        setLoading(true);
        addHistory();
        console.log("sending", search);
        const response = await fetch({search: search})
        console.log("final", response);
        setLoading(false);
    };

    const onData = useCallback((result) => {
        console.log("onData", result);
        const data = result?.data;
        if (!data?.result?.msg)
            return;
        addHistory({ "type": "response", "text": data.result.msg, "id": crypto.randomUUID() });
    });

    
    const { data, error } = useGraphQLSubscription({
        url: 'ws://localhost:8000/gql', 
        query: subscriptionQuery,
        onData: onData
    });

    return (
        <div>
            {history.map(item => <HistoryItem key={item.id} {...item} />
            )}
            <div className="form-floating mb-3 mt-3">
                <AutoGrowTextarea id="query" className='form-control' onChange={onChange} value={search} />
                <label htmlFor="query">Co mám vyhledat</label>
            </div>
            {(loading || query_loading) && <Loader />}
            {!(loading || query_loading) && <button className="form-control btn btn-outline-primary" onClick={onSend}>Odeslat</button>}
        </div>
    );
};
