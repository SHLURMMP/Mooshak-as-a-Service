import './Styles.css'
import axios from "axios";
import { useEffect, useState } from 'react';
//import { ContestTable }from './components/ContestTable '

function MainPage() {

  const ContestCreation = () => {
    
    window.location.href = '/contestcreation/';
  };

  const ContestManagment = (id) => {
    
    window.location.href = '/contestdetails/' + id;
  };

  const [contests, setContests] = useState([]);
  const [showTable, setShowTable] = useState(false)
  

  const fetchData = () => {
    axios
       .get('/api/contestsinfo')
       .then((response) => {
          
          if(response.data.contests.length){
            setContests(response.data.contests);
            setShowTable(!showTable)
            console.log(!showTable)
          }

       })
       .catch((err) => { 
          console.log(err);
       });
  }


  useEffect( () => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 15000);

    return () => clearInterval(interval);
 }, []);

    return (
      <div className="Page text-center">
        <div className="Header">
          <button onClick={() => ContestCreation()} class = 'Button btn btn-primary'>Create Contest</button>
        </div>
        {showTable ? 
        <table className="ContestTable table-hover table-striped table-bordered">
        <thead className='ContestTableHeader'>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>URL</th>
            <th>Status</th>
            <th>Number of Teams</th>
            
          </tr>
        </thead>
        <tbody className='ContestTableBody'>
          {
            contests.map((contest, index) => (
              <tr key = {index}>
                <td>{contest.title}</td>
                <td>{contest.description}</td>
                <td>{contest.url}</td>
                <td>{contest.is_online ? 'Online' : 'Offline'}</td>
                <td>{contest.number_teams}</td>
                <td><button onClick={() => ContestManagment(contest.id)} class = 'Button btn btn-primary focus-ring'>Manage</button></td>
              </tr>
            )
            )
          }
        </tbody>
      </table> : 
      <p>You haven't created an environment yet.</p>}
      </div>
      
    );

}
export default MainPage;