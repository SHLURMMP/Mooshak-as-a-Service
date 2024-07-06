import React, { useEffect, useState } from 'react';
//import { UNSAFE_DataRouterStateContext } from "react-router-dom";


function ContestCreationError(){


    const MainPage = () => {
        window.location.href = '/';
    };

    return(
        <div>
            <h1>Erro ao Criar Concurso</h1>
            <button onClick={() => MainPage()}>Voltar à Página Inicial</button>
        </div>
    );
}
export default ContestCreationError;