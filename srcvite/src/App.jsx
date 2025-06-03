import React, { useRef, useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';

import { SearchApp } from "./SearchApp"
import { DocAdd } from "./DocAdd"

export const App = () => {
  const [app, setApp] = useState(0)
  const handleClick = (value) => () => setApp(value)
  return (
    <div className="container mt-5">
      {app == 1 && <button className="btn btn-outline-primary form-control" onClick={handleClick(0)}>Search</button>}
      {app == 0 && <button className="btn btn-outline-primary form-control" onClick={handleClick(1)}>Přidávat dokumenty</button>}
      {app == 1 && <DocAdd />}
      {app == 0 && <SearchApp />}
    </div>
  );
};
