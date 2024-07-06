import './Styles.css'
import axios from "axios";
import React, { useEffect, useState } from 'react';
import { UNSAFE_DataRouterStateContext } from "react-router-dom";
import { useParams } from 'react-router-dom';


function ContestEdit(){

    const { id } = useParams();
    const [contestInfo, setContestInfo] = useState({title: '', description: '', contest_specs: 't2.micro'});
    const [disable, setDisable] = useState(false);

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
        await axios.put('/edit/contest', contestInfo, {
            headers: {
                'contest': id
            }
        })
        .then(
            (response) => {
                console.log(response)
                MainPage()
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

    return(
        <div className="Page text-center">
            <h1>Edit Contest</h1>
            
            <form onSubmit={handleSubmit}>
                <div class="form-group">
                    <label for="title">Contest Name</label>
                    <input type="text" name="title" required value={contestInfo.title} onChange={handleChange} class="form-control"/>
                </div>
                <div class="form-group">
                    <label for="description">Contest Description</label>
                    <input type="text" name="description" required value={contestInfo.description} onChange={handleChange} class="form-control"/>
                </div>
                <div class="form-group">
                    <p>Contest Server Specs:</p>
                    <select name = "contest_specs" onChange={handleChange} class="form-control">{serverConf.map((conf) => {
                        return <option value = {conf.name}>{conf.specs}</option>
                    })}</select>
                </div>
                <p></p>
                <input type="submit" value = 'Edit' disabled = {disable}  class='btn btn-primary'/>
            </form>
        </div>
    );


}
export default ContestEdit;