const { PAYMENT_STATUS } = require('../config/constants');

module.exports = ({ reportModel }) => ({
  async financialReport() {
    const rows = await reportModel.financialRows();
    const courses = new Map();

    for (const row of rows) {
      if (!courses.has(row.course_id)) {
        courses.set(row.course_id, { course: row.title, revenue: 0, students: [] });
      }
      if (row.enrollment_id === null) continue; // curso sem matrículas

      const entry = courses.get(row.course_id);
      if (row.status === PAYMENT_STATUS.PAID) entry.revenue += row.amount;
      entry.students.push({ student: row.student ?? 'Unknown', paid: row.amount ?? 0 });
    }
    return [...courses.values()];
  },
});
