import React, {useState} from 'react';
import Chart from '../Chart/Chart';
import {KPI} from "../../api/DataStructures";
import {fetchData} from "../../api/DataFetcher";
import FilterOptions, {Filter} from "../Selectors/FilterOptions";
import {TimeFrame} from "../Selectors/TimeSelect"
import PersistentDataManager from "../../api/DataManager";
import DataManager from "../../api/DataManager";
import KpiSelect from "../Selectors/KpiSelect";
import GraphTypeSelector from "../Selectors/GraphTypeSelector";
import AdvancedTimeSelect from "../Selectors/AdvancedTimeSelect";


const KpiSelector: React.FC<{
    kpi: KPI;
    setKpi: (value: KPI) => void;
    timeFrame: TimeFrame;
    setTimeFrame: (value: TimeFrame) => void;
    graphType: string;
    setGraphType: (value: string) => void;
    filters: Filter;
    setFilters: (filters: Filter) => void;
    onGenerate: () => void;
    dataManager: PersistentDataManager;
}> = ({
          kpi,
          setKpi,
          timeFrame,
          setTimeFrame,
          graphType,
          setGraphType,
          filters,
          setFilters,
          onGenerate,
          dataManager
      }) => {
    return (
        <section className="p-6 mx-auto space-y-10 bg-white shadow-md rounded-lg">
            {/* KPI, Time Frame and Graph Type Selectors in one line */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* KPI Selector */}
                <KpiSelect
                    label="KPI"
                    description={`Select the KPI you want to visualize`}
                    value={kpi}
                    options={dataManager.getKpiList()}
                    onChange={setKpi}
                />

                {/* Time Frame Selector */}
                <AdvancedTimeSelect timeFrame={timeFrame} setTimeFrame={setTimeFrame}/>

                {/* Graph Type Selector */}
                <div className="flex items-center justify-center">
                    <GraphTypeSelector value={graphType} onChange={setGraphType}/>
                </div>
            </div>

            {/* Filters Section */}
            <FilterOptions filter={filters} onChange={setFilters}/>

            {/* Generate Button */}
            <div className="text-center">
                <button
                    onClick={onGenerate}
                    className="bg-blue-500 text-white px-6 py-2 rounded shadow hover:bg-blue-600 transition"
                >
                    Generate Chart
                </button>
            </div>
        </section>
    );
};

const DataView: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [kpi, setKpi] = useState<KPI>(dataManager.getKpiList()[0]);
    const [timeFrame, setTimeFrame] = useState<TimeFrame>({
        from: new Date(2024, 2, 2),
        to: new Date(2024, 9, 19),
        aggregation: "month"
    });
    const [graphType, setGraphType] = useState('pie');
    const [filters, setFilters] = useState<Filter>(new Filter('All', []));
    const [chartData, setChartData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    // Used to store the last used chart type and not sync the chart to the selected one before the new data is fetched
    const [usedChartType, setUsedChartType] = useState('pie');
    // Function to fetch chart data with applied filters

    const fetchChartData = async () => {
        try {
            setLoading(true);
            //sync the chart type with the last used one
            setGraphType(usedChartType);
            // if one of the parameters is not set, return
            if (kpi && timeFrame && graphType && DataManager.getInstance().getMachineList()) {
                const data = await fetchData(kpi, timeFrame, usedChartType, filters);
                setChartData(data);
            }
        } catch (e) {
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-1 flex-col w-full h-full space-y-5 p-6 items-center">
            {/* KPI Selector and Generate Button */}
            <KpiSelector
                kpi={kpi}
                setKpi={setKpi}
                timeFrame={timeFrame}
                setTimeFrame={setTimeFrame}
                graphType={usedChartType}
                setGraphType={setUsedChartType}
                filters={filters}
                setFilters={setFilters}
                onGenerate={fetchChartData} // Fetch chart data when "Generate" button is clicked
                dataManager={dataManager}
            />

            {/* Chart Section */}

            {loading ? <p>Loading...</p> :
                <div className={` shadow-md p-5 bg-white flex w-auto`}>
                    <Chart data={chartData} graphType={graphType} kpi={kpi} timeUnit={timeFrame.aggregation}/>
                </div>
            }
        </div>
    );
};

export default DataView;