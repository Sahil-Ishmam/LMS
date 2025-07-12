import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { Children } from "react";

const PrivateRoute = ({ Children }) => {
  const loggedIn = useAuthStore((state) => state.isLoggedIn)();
  return loggedIn ? <>{Children}</> : <Navigate to="/login/" />;
};
export default PrivateRoute;
