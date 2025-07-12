import { Children, useEffect, useState } from "react";
import { setUser } from "../utils/auth";

const MainWrapper = ({Children}) =>{
    const [loading,setLoading] = useState(true);

    useEffect(()=>{
        const handler = async () =>{
            setLoading(true);

            await setUser;

            setLoading(false);

        };
        handler();
    },[]);


    return <>{loading?null:Children}</>
}


export default MainWrapper;