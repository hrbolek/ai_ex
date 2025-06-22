import { useRef } from 'react';


export const AutoGrowTextarea = (props) => {
    const ref = useRef();

    function handleChange(e) {
        if (ref.current) {
            ref.current.style.height = "auto";
            ref.current.style.height = ref.current.scrollHeight + "px";
        }
        props.onChange(e);
    }

    return (
        <textarea
            ref={ref}
            {...props}
            onChange={handleChange}
            style={{ overflow: "hidden", minHeight: 40 }} />
    );
};
