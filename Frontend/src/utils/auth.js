import { useAuthStore } from "../store/auth";
import axios from "./axios";
import jwt_decode from "jwt-decode";
import Cookie from "js-cookie";
import Swal from "sweetalert2";

export const login = async (email, password) => {
  try {
    const { data, status } = await axios.post(`user/token/`, {
      email,
      password,
    });
    if (status == 200) {
      setAuthUser(data.access, data.refresh);
      // alert("Loging Successful");
    }

    return { data, error: null };
  } catch (error) {
    return {
      data: null,
      error: error.response.data?.detail || "something went wrong",
    };
  }
};

export const register = async (full_name, email, password, password2) => {
  try {
    const { data } = await axios.post(`user/register/`, {
      full_name,
      email,
      password,
      password2,
    });
    // automatically login the user
    await login(email, password);
    // alert("Registration successfully");
    return { data, error: null };
  } catch (error) {
    return {
      data: null,
      error:
        `${error.response.data.full_name} - ${error.response.data.email}` ||
        "something went wrong",
    };
  }
};

export const logout = () => {
  Cookie.remove("access_token");
  Cookie.remove("refresh_token");
  useAuthStore.getState().setUser(null);
  // alert("You have been logged out");
};

export const setUser = async () => {
  const access_token = Cookie.get("access_token");
  const refresh_token = Cookie.get("refresh_token");

  if (!access_token || !refresh_token) {
    // alert("Tokens doens't exists");
    return;
  }
  if (isAccessTokenExpaired(access_token)) {
    const response = await getRefreshedToken(refresh_token);
    setAuthUser(response.access, response.refresh);
  } else {
    setAuthUser(access_token, refresh_token);
  }
};

export const setAuthUser = (access_token, refresh_token) => {
  Cookie.set("access_token", access_token, {
    expires: 1,
    secure: true,
  });

  Cookie.set("refresh_token", refresh_token, {
    expires: 7,
    secure: true,
  });

  const user = jwt_decode(access_token) ?? null;

  if (user) {
    useAuthStore.getState().setUser(user);
  }
  useAuthStore.getState().setLoading(false);
};

export const getRefreshedToken = async () => {
  const refresh_token = Cookie.get("refresh_token");
  const response = await axios.post(`token/refresh/`, {
    refresh: refresh_token,
  });

  return response.data;
};

export const isAccessTokenExpaired = (access_token) => {
  try {
    const decodedToken = jwt_decode(access_token);
    return decodedToken.exp < Date.now() / 1000;
  } catch (error) {
    console.log(error);
    return true;
  }
};
