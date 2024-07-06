import './Styles.css'
import React, { useState, useEffect } from 'react';
import axios from "axios";
import { useParams } from 'react-router-dom';

function ContestStatus(){
   
    const { id } = useParams();
    const [contestStatus, setContestStatus] = useState([]);

    const ContestPage = () => {    
        window.location.href = '/contestdetails/' + id;
        console.log('here')
    };

    const fetchData = () => {
        axios
            .get('/api/conteststatus',{
                headers: {
                    'contest': id
                }
            })
            .then((response) => {
              
                setContestStatus(response.data);

            })
            .catch((err) => { 
              console.log(err);
            });
    }

    useEffect(() => {
        fetchData();
        const interval = setInterval(() => {
            fetchData();
        }, 15000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className='Page'> 
            <h1>Health Status of {contestStatus.contest}</h1>
            <div class='InfoSection'>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Instance Status is related to the internal functionality of the instance, like its reachability.</div>
                </div>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Instance Status: {contestStatus.InstanceStatus ? contestStatus.InstanceStatus.Status : ''}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Test Results: {contestStatus.InstanceStatus ? contestStatus.InstanceStatus.Details[0].Status : ''}</div>
                </div>
                {contestStatus.InstanceStatus ? (contestStatus.InstanceStatus.Details[0].ImpairedSince ? 
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Impaired Since: {contestStatus.InstanceStatus.Details[0].ImpairedSince}</div>
                </div> : '') :''}
                
            </div>
            <p></p>
            <div class='InfoSection'>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>System Status is related to the functionality of the systems that support an instance, like hardware or network connectivity.</div>
                </div>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>System Status: {contestStatus.SystemStatus ? contestStatus.SystemStatus.Status : ''}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Test Results: {contestStatus.SystemStatus ? contestStatus.SystemStatus.Details[0].Status : ''}</div>
                </div>
                {contestStatus.SystemStatus ? (contestStatus.SystemStatus.Details[0].ImpairedSince ? 
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Impaired Since: {contestStatus.SystemStatus.Details[0].ImpairedSince}</div>
                </div> : '') : ''}
            </div>
            <div><button onClick={ContestPage} class = 'btn btn-primary'>Return to Contest Page</button></div>
        </div>
    );
}
export default ContestStatus;