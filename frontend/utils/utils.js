export const startYear = 2000;
export const oneDay = 86400;

export function generateDateObject() {
    const currentDate = new Date();
    let yearData = {};

    for (let i = startYear; i <= currentDate.getFullYear(); i++) {
        let monthData = {};
        for (let j = 1; j <= 12; j++) {
            let days = new Date(i, j, 0).getDate();
            let daysData = {}
            for (let day = 1; day <= days; day++) {
                let a = {};
                [...Array(24).keys()].map((i) => i + 1)
                    .forEach((item) => {
                        a[item] = null
                    });
                daysData[day] = a;
            }
            monthData[j] = daysData;
        }
        yearData[i] = monthData;
    }
    return (yearData);
}
