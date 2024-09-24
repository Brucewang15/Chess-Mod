import logo from './logo.svg';
import './App.css';

import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import ChessMain from "./components/ChessMain";

function App() {
  return (
      <div className="App">

          <BrowserRouter>

              <Routes>
                  <Route path="/" element={<ChessMain/>}/>
              </Routes>

          </BrowserRouter>


          {/*<h1 className="text-3xl bg-green-200 font-bold underline">*/}
          {/*    Hello world!*/}
          {/*</h1>*/}

      </div>
  );
}

export default App;
