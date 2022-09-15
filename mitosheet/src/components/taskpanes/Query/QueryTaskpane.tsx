// Copyright (c) Mito

import React from 'react';
// Import
import MitoAPI from '../../../jupyter/api';
import { AnalysisData, UIState, UserProfile } from '../../../types';
import Row from '../../layout/Row';
import DefaultTaskpane from '../DefaultTaskpane/DefaultTaskpane';
import DefaultTaskpaneBody from '../DefaultTaskpane/DefaultTaskpaneBody';
import DefaultTaskpaneFooter from '../DefaultTaskpane/DefaultTaskpaneFooter';
import DefaultTaskpaneHeader from '../DefaultTaskpane/DefaultTaskpaneHeader';
import TextButton from "../../elements/TextButton";
import { classNames } from "../../../utils/classNames";

interface QueryTaskpaneProps {
    mitoAPI: MitoAPI;
    userProfile: UserProfile;
    setUIState: React.Dispatch<React.SetStateAction<UIState>>;
    analysisData: AnalysisData;
}

type QueryTaskpaneState = {
    path: string;
    instruments: string;
    fields: string;
    start_date: string;
    end_date: string;
}


function QueryTaskpane(props: QueryTaskpaneProps): JSX.Element {

    const [queryState, setQueryState] = React.useState<QueryTaskpaneState>({
        path: "",
        instruments: "",
        fields: "",
        start_date: "",
        end_date: ""
    })

    async function query(): Promise<void> {

        const instruments = queryState.instruments.split(",");
        const fields = queryState.fields.split(",");
        const possibleMitoError = await props.mitoAPI.editQuery(
            queryState.path,
            instruments,
            fields,
            queryState.start_date,
            queryState.end_date
        );
        console.log(possibleMitoError)
    }

    return (
        <DefaultTaskpane>
            <DefaultTaskpaneHeader
                header='Query Data'
                setUIState={props.setUIState}
            />
            <DefaultTaskpaneBody noScroll>
                <div className="mt-5px mb-10px">
                    <label htmlFor="dataPath" className="mb-5px block">
                        Data Path
                    </label>
                    <input
                        id="dataPath"
                        className={classNames('mito-input', 'text-body-2', 'element-width-block')}
                        placeholder="Data folder..."
                        value={queryState.path}
                        onChange={(e) => setQueryState({ ...queryState, path: e.target.value })}
                    ></input>
                </div>
                <div className="mt-5px mb-10px">
                    <label htmlFor="instruments" className="mb-5px block">
                        Instruments
                    </label>
                    <input
                        id="instruments"
                        className={classNames('mito-input', 'text-body-2', 'element-width-block')}
                        placeholder="instrument list..."
                        value={queryState.instruments}
                        onChange={(e) => setQueryState({ ...queryState, instruments: e.target.value })}
                    ></input>
                </div>
                <div className="mt-5px mb-10px">
                    <label htmlFor="fields" className="mb-5px block">
                        Fields
                    </label>
                    <input
                        id="fields"
                        className={classNames('mito-input', 'text-body-2', 'element-width-block')}
                        placeholder="fields list..."
                        value={queryState.fields}
                        onChange={(e) => setQueryState({ ...queryState, fields: e.target.value })}
                    ></input>
                </div>
                <div className="mt-5px mb-10px">
                    <label htmlFor="startDate" className="mb-5px block">
                        Start Date
                    </label>
                    <input
                        id="startDate"
                        className={classNames('mito-input', 'text-body-2', 'element-width-block')}
                        placeholder="start date..."
                        value={queryState.start_date}
                        onChange={(e) => setQueryState({ ...queryState, start_date: e.target.value })}
                    ></input>
                </div>
                <div className="mt-5px mb-10px">
                    <label htmlFor="endDate" className="mb-5px block">
                        End Date
                    </label>
                    <input
                        id="endDate"
                        className={classNames('mito-input', 'text-body-2', 'element-width-block')}
                        placeholder="end date..."
                        value={queryState.end_date}
                        onChange={(e) => setQueryState({ ...queryState, end_date: e.target.value })}
                    ></input>
                </div>
            </DefaultTaskpaneBody>
            <DefaultTaskpaneFooter>
                <Row justify='space-between'>
                    <TextButton
                        variant='dark'
                        width='block'
                        onClick={() => query()}
                    >
                        Submit
                    </TextButton>
                </Row>
            </DefaultTaskpaneFooter>
        </DefaultTaskpane >
    )
}

export default QueryTaskpane;