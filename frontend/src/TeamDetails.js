import Notification from './Notification';
import './Styles.css'
import React, { useState, useEffect } from 'react';
import axios from "axios";
import { useParams } from 'react-router-dom';

function TeamDetails (){

    const { id } = useParams();
    const [team, setTeam] = useState({});
    const [status, setStatus] = useState('');
    const [notification, setNotification] = useState(false);
    const [disable, setDisable] = useState(false);

    const ContestDetails = (id) => {
        window.location.href = '/contestdetails/' + id;
    }
    

    const fetchData = () => {
        axios
            .get('/api/team/'+ id)
            .then((response) => {
              
                setTeam(response.data.team);
                console.log(response.data.team)

            })
            .catch((err) => { 
              console.log(err);
            });
    }

    useEffect(() => {
        fetchData();
        const interval = setInterval(() => {
            fetchData();
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const createEnvironment = () => {
        setDisable(true)
        const teams = [team]
        
        axios.post('/create/environment', teams)
        .then(
            (response) => {
                console.log(response.data)
                fetchData()
                setDisable(false)
                //setNotification('Environment in creation process')
            }
        )
    }

    const rebootEnvironment = (id) => {
        setDisable(true)

        if (team.environment.is_online == true){
            setStatus('Environment is stopping')
        }
        else if (team.environment.is_online == false){
            setStatus('Environment is starting')
        }
        setNotification(true)

        axios.get('/reboot/environment', {
            headers: {
                'team': id
            }
        })
        .then(
            (response) => {
                console.log(response.data)
                fetchData()
                setDisable(false)
                setNotification(false)
            }
        )
    }

    const deleteTeam = (id) => {
        setDisable(true)
        setStatus('Team being deleted')
        setNotification(true)
        axios.delete('/delete/team', {
            headers: {
                'team': id
            }
        })
        .then(
            (response) => {
                ContestDetails(team.contest)
            }
        )
    }


    const deleteEnvironment = (id) => {
        setDisable(true)
        setStatus('Environment being deleted')
        setNotification(true)
        axios.delete('/delete/environment', {
            headers: {
                'team': id
            }
        })
        .then(
            (response) => {
                fetchData()
                setDisable(false)
                setNotification(false)
            }
        )
    }

    return(
        <div className='Page'>
            <h1>{team.title}</h1>
            <div class='InfoSection'>
                <div class='InfoBlock'>
                    <div class='teamInfo'>Email: {team.email}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='teamInfo'>Contest Password: {team.mooshak_password ? team.mooshak_password : 'N/A'}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='teamInfo'>Environment Name: {(team.has_env) ? team.environment.name : 'N/A'}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='teamInfo'>Environment password: {(team.has_env) ? team.environment.password : 'N/A'}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='teamInfo'>Environment IP: {(team.has_env) ? team.environment.ipv4_address : 'N/A'}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='teamInfo'>Status: {(team.has_env)  ? (team.environment.is_online ? 'Online' : 'Offline') : 'N/A'}</div>
                </div>
            </div>
            <div>
                {(!team.has_env) ? //se tem ambiente
                <div>
                    <button onClick={() => createEnvironment()} disabled = {disable} class = 'btn btn-primary'>Create Environment</button>
                    <button onClick={() => deleteTeam(team.id)} disabled = {disable} class = 'btn btn-primary'>Delete Team</button>
                    <button onClick={() => ContestDetails(team.contest)} disabled = {disable} class = 'btn btn-primary'>Return to Contest Page</button>
                </div>
                :
                <div>
                    <button onClick={() => rebootEnvironment(team.id)} disabled = {disable} class = 'btn btn-primary'>Start/Stop Environment</button>
                    <button onClick={() => deleteEnvironment(team.id)} disabled = {disable} class = 'btn btn-primary'>Delete Environment</button>
                    <button onClick={() => deleteTeam(team.id)} disabled = {disable} class = 'btn btn-primary'>Delete Team</button>
                    <button onClick={() => ContestDetails(team.contest)} disabled = {disable} class = 'btn btn-primary'>Return to Contest Page</button>
                </div>
                }
            </div>
            <Notification trigger = {notification} setTrigger = {setNotification}>
                <h3>{status}</h3>
            </Notification>
        </div>
    );

}
export default TeamDetails;