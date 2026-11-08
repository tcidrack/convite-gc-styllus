import { Routes, Route } from "react-router-dom"
import Splash from "./pages/Splash"
import Invite from "./pages/Invite"
import Admin from "./pages/Admin"

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Splash />} />
      <Route path="/convite" element={<Invite />} />
      <Route path="/admin" element={<Admin />} />
    </Routes>
  )
}
