import axios from "axios";
import { getRefreshedToken, isAccessTokenExpaired, setAuthUser } from "./auth";
import { API_BASE_URL } from "./constants";
import Cookies from "js-cookie";

const useAxios = () => {
  const access_token = Cookies.get("access_token");
  const refresh_token = Cookies.get("refresh_token");

  const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      Authorization: `Bearer ${access_token}`,
    },
  });

  axiosInstance.interceptors.request.use(async (req) => {
    if (!isAccessTokenExpaired(access_token)) {
      return req;
    }

    // const response = await getRefreshedToken(refresh_token);
    const response = getRefreshedToken(refresh_token);

    setAuthUser(response.access, response.refresh);
    req.headers.Authorization = `Bearer ${response.data?.access}`;
    return req;
  });

  return axiosInstance;
};

export default useAxios;
