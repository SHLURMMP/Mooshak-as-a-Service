import './Styles.css'
import Notification from './Notification';
import React, { useState, useEffect } from 'react';
import axios from "axios";
import { useParams } from 'react-router-dom';
import { jsPDF } from "jspdf";
import autoTable from 'jspdf-autotable'

function ContestDetails (){

    const { id } = useParams();
    const [contest, setContest] = useState([]);
    const [hasTeams, setTeams] = useState(false);
    const [notification, setNotification] = useState(false);
    const [status, setStatus] = useState('');
    const [disable, setDisable] = useState(false);


    const MainPage = () => {
    
        window.location.href = '/';
        console.log('here')
    };

    const ContestStatus = (id) => {
        window.location.href = '/conteststatus/' + id;
    };

    const TeamDetail = (id) => {
        window.location.href = '/teamdetails/' + id;
    };

    const ContestEdit = (id) => {
        window.location.href = '/contestedit/' + id;
    }

    const fetchData = () => {
        axios
            .get('/api/contests/'+ id)
            .then((response) => {
              
                setContest(response.data.contest);

                //console.log(response.data.contest.teams)
                //if contest has teams -> hasTeams = True
                if(response.data.contest.teams.length){
                    setTeams(!hasTeams);
                }

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

    const DeleteContest = (id) => {
        setDisable(true)
        setStatus('Contest is being Deleted')
        setNotification(true)

        axios.delete('/delete/contest',{
            headers: {
                'contest': id
            }
        })
        .then(
            (response) => {
                setDisable(false)
                MainPage()
            }
        )
        .catch((err) => { 
            console.log(err);
        });
    }

    const RebootContest = (id) => {
        setDisable(true)

        console.log(contest.is_online)
        if (contest.is_online == true){
            setStatus('Environment is stopping')
        }
        else if (contest.is_online == false){
            setStatus('Environment is starting')
        }
        setNotification(true)

        axios.get('/reboot/contest',{
            headers: {
                'contest': id
            }
        })
        .then(
            (response) => {
                console.log(response)
                fetchData()
                setDisable(false)
                setNotification(false)
            }
        )
        .catch((err) => { 
            console.log(err);
        });
    }

    const CreateBulkEnvironments = () => {
        setDisable(true)
        setStatus('Environments in creation')
        setNotification(true)

        axios.post('/create/environment', contest.teams)
        .then(
            (response) => {
                fetchData()
                console.log(response)
                setDisable(false)
                setNotification(false)
            }
        )
    }

    const ImportTeams = (id) => {
        setStatus('Teams being imported')
        setNotification(true)

        axios.get('/import/teams',{
            headers: {
                'contest': id
            }
        })
        .then(
            (response) => {
                fetchData()
                setNotification(false)
            }
        )
        .catch((err) => { 
            console.log(err);
        });
    }

    const ExportPDF = async () => {

        var teams = []
        
        contest.teams.forEach((element) => {
            teams.push([element.title, element.email, element.environment.name, element.environment.password, element.mooshak_password])
        });
        
        var doc = new jsPDF()
        
        doc.setFontSize(18)
        doc.text('Tabela de Equipas', 14, 22)
        doc.setFontSize(11)
        doc.setTextColor(100)

        var pageSize = doc.internal.pageSize
        var pageWidth = pageSize.width ? pageSize.width : pageSize.getWidth()
        var text = doc.splitTextToSize("Para aceder ao ambiente de equipa atribuído, diriga-se a https://eu-west-1.webclient.amazonworkspaces.com/registration, introduza o código de registo wsdub+6MXMUN e faça login com o nome da equipa e password atribuída.",
        pageWidth - 35, {})
        doc.text(text, 14, 30)

        doc.autoTable({
            head:[['Nome de Equipa', 'Email', 'Nome de Ambiente', 'Password de Ambiente', 'Password de Mooshak']],
            body:teams,
            startY: 50,
            showHead: 'firstPage',
        })
        
        doc.save('equipas.pdf')
    };

    return(
        <div className='Page'>
            <h1>{contest.title}</h1>
            <div class='InfoSection'>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Description: {contest.description}</div>
                    
                </div>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>URL: </div>
                    <div class='InfoLabel'>{contest.url}</div>
                </div>
                <div class='InfoBlock'>
                    <div class='InfoLabel'>Status: </div>
                    <div class='InfoLabel'>{contest.is_online ? 'Online' : 'Offline'}</div>
                </div>
            </div>
            <div>
                <button onClick={() => ContestEdit(id)} disabled = {disable} class = 'btn btn-primary'>Edit</button>
                <button onClick={() => DeleteContest(id)} disabled = {disable} class = 'btn btn-primary'>Delete</button>
                <button onClick={() => RebootContest(id)} disabled = {disable} class = 'btn btn-primary'>Start/Stop Server</button>
                <button onClick={() => ContestStatus(id)} disabled = {disable} class = 'btn btn-primary'>Check Server Health</button>
            </div>
            {hasTeams ? 
            <div>
                <table className="TeamTable table-hover table-striped table-bordered" id = "team_data">
                <thead>
                <tr>
                    <th>Team Name</th>
                    <th>Team Email</th>
                    <th>Contest Password</th>
                    <th>Environment Created</th>
                </tr>
                </thead>
                <tbody>
                {
                    contest.teams.map((team, index) => (
                    <tr key = {index}>
                        <td>{team.title}</td>
                        <td>{team.email}</td>
                        <td>{team.mooshak_password ? team.mooshak_password : 'Not Available'}</td>
                        <td>{team.has_env ? 'Yes' : 'No'}</td>   
                        <td><button onClick={() => TeamDetail(team.id)} class = 'btn btn-primary'>Manage</button></td>
                    </tr>
                    )
                    )
                }
                </tbody>
                </table>
                <button onClick={ExportPDF} disabled = {disable} class = 'btn btn-primary'>Export PDF</button>
                <button onClick={CreateBulkEnvironments} disabled = {disable} class = 'btn btn-primary'>Create Team Environments</button>
                <button onClick={MainPage} disabled = {disable} class = 'btn btn-primary'>Return to Main Page</button>
            </div> : 
            <div>
                <p>No teams have been imported.</p>
                <button onClick={() => ImportTeams(id)} disabled = {disable} class = 'btn btn-primary'>Import Teams</button>
                <button onClick={MainPage} disabled = {disable} class = 'btn btn-primary'>Return to Main Page</button>
            </div>
                
            }
            <Notification trigger = {notification} setTrigger = {setNotification}>
                <h3>{status}</h3>
            </Notification>
        </div>
    );

}
export default ContestDetails;