import './Styles.css'
import axios from "axios";
import React, { useEffect, useState } from 'react';
import Papa from "papaparse";
//import { UNSAFE_DataRouterStateContext } from "react-router-dom";


function ContestCreation(){

    const [fileData, setFileData] = useState([]);
    const [disable, setDisable] = useState(false);

    const [contestInfo, setContestInfo] = useState({title: '', description: '', contest_specs: 't2.micro', admin_password: '', judge_password: '', teams: []});

    const serverConf = [{'name' : 't2.micro' ,'specs' : '1 CPUs, 1Gb RAM'},
                        {'name' : 't2.medium' ,'specs' : '2 CPUs, 4Gb RAM'},
                        {'name' : 't2.large' ,'specs' : '2 CPUs, 8Gb RAM'},
                        {'name' : 't2.xlarge' ,'specs' : '4 CPUs, 16Gb RAM'}
                    ]

    const MainPage = () => {    
        window.location.href = '/';
        console.log('here')
      };

    const ContestCreationError = () => {
        window.location.href = '/contestcreationerror';
        console.log('here')
    }

    const hideSubmit = () => {
        setDisable(true);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        hideSubmit();
        await axios.post('/create/contest', contestInfo)
        .then(
            (response) => {
                console.log(response)
                if (response.data != null) {
                    MainPage() 
                }
                 
            }     
        )
        .catch((err) => { 
            ContestCreationError();
         });
        console.log(contestInfo)
    };

    const handleChange = (event) => {
        const { name, value } = event.target;
        setContestInfo((prevState) => ({ ...prevState, [name]: value }));
    };

    const handleFileChange = (event) => {
        if (event.target.files.length) {
            const file = event.target.files[0]

            Papa.parse(file, {
                header: true,
                complete: (results) => {
                    setFileData((prevState) => (results.data));
                    console.log(results.data)
                    //console.log(fileData);
                    contestInfo['teams'] = results.data
                },
            });
            //console.log(contestInfo);
        }     
    };

    return(
        <div className="Page text-center">
            <h1>Contest Creation</h1>
            
            <form onSubmit={handleSubmit}>
                <div class="form-group">
                    <label for="title">Contest Name</label>
                    <input type="text" required name="title" value={contestInfo.title} onChange={handleChange} class="form-control"/>
                </div>
                <div class="form-group">
                    <label for="description">Contest Description</label>
                    <input type="textarea" required name="description" value={contestInfo.description} onChange={handleChange} class="form-control"/>
                </div> 
                <div class="form-group">
                    <label for="admin_password">Admin Password</label>
                    <input type="password" required name="admin_password" value={contestInfo.admin_password} onChange={handleChange} class="form-control"/>
                </div>
                <div class="form-group">
                    <label for="judge_password">Judge Password</label>
                    <input type="password" required name="judge_password" value={contestInfo.judge_password} onChange={handleChange} class="form-control"/>
                </div>
                <div class="form-group">
                    <label for="contest_specs">Contest Server Specs</label>
                    <select name = "contest_specs" onChange={handleChange} class="form-control">{serverConf.map((conf) => {
                        return <option value = {conf.name}>{conf.specs}</option>
                    })}</select>
                </div>
                <div class="form-group">
                    <label for="csvFileInput">Teams File</label>
                    <input type="file" name="csvFileInput" accept=".csv" onChange={handleFileChange} class="form-control-file"/>
                </div>
                <p></p>
                
                <input type="submit" value = 'Create' disabled = {disable} class='btn btn-primary'/>
            </form>
        </div>
    );


}
export default ContestCreation;