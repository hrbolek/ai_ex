import ReactMarkdown from "react-markdown";

export const HistoryItem = ({type, text}) => {
    if (type === "userPrompt") {
        return (
            <div className='row'>
                <div className='col col-md-3'></div>
                <div className='col col-md-9'>
                    <div className='alert alert-primary'>{text}</div>
                </div>
            </div>
            
        )

    } else {
        return (
            <div className='alert alert-success'>
                <ReactMarkdown>
                    {text}
                </ReactMarkdown>
            </div>
        )
    }

}
