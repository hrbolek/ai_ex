
export const Loader = ({ text = "Přemýšlím" }) => (
    <div className="chatgpt-loader">
        {text}
        <span className="dots">
            <span>.</span><span>.</span><span>.</span>
        </span>
        <style>
            {`
        .chatgpt-loader .dots span {
            opacity: 0;
            animation: dotFlashing 1.2s infinite linear;
            font-weight: bold;
        }
        .chatgpt-loader .dots span:nth-child(1) { animation-delay: 0s }
        .chatgpt-loader .dots span:nth-child(2) { animation-delay: 0.2s }
        .chatgpt-loader .dots span:nth-child(3) { animation-delay: 0.4s }
        @keyframes dotFlashing {
            0%, 80%, 100% { opacity: 0; }
            40% { opacity: 1; }
        }
        `}
        </style>
    </div>
);
