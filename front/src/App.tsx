
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Channel from "./page/Channel";
import CreateChannel from "./page/CreateChannel";
import GetToken from "./page/GetToken";
import GetUserInfo from "./page/GetUserInfo";
import Lobby from "./page/Lobby";
import KakaoLogin from "./page/KakaoLogin";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<KakaoLogin />} />
        <Route path="/lobby" element={<Lobby />} />
        <Route path="/getToken" element={<GetToken />} />
        <Route path="/getUserInfo" element={<GetUserInfo />} />
        <Route path="/channel" element={<Channel />} />
        <Route path="/channel/create" element={<CreateChannel />} />
      </Routes>
    </Router>
  );
}

