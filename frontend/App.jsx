import 'bootstrap/dist/css/bootstrap.min.css';
import { useEffect, useState } from 'react';
import { SearchPage } from './Search';

export const ManageDocuments = () => {
    return (
        <div>Manage</div>
    )
}

const map = {
    "Search": SearchPage,
    "Manage": ManageDocuments
}

export const App = () => {
    const [state, setState] = useState("Search")
    const Component = map[state]
    return (
        <div className='container'>
            <div className='mt-4 p-5 bg-primary text-white rounded'>
                <h1>Radílek</h1>
            </div>
            <Component />
        </div>
    )
}