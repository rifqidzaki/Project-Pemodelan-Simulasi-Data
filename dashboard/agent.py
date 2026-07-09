import random
from mesa import Agent

class StudentAgent(Agent):
    """
    Agen merepresentasikan calon mahasiswa.
    Bergerak di grid, berinteraksi dengan agen lain,
    dan membuat keputusan pemilihan jurusan.
    """
    
    CBT_TECHNIQUES = {
        'konseling_akademik': 0.55,
        'tes_minat_bakat':    0.50,
        'guru_BK':            0.45,
        'seminar_jurusan':    0.40,
        'mentoring':          0.35,
    }

    def __init__(self, unique_id, model, minat=None, kemampuan=None, sosial=None, kebingungan=None):
        super().__init__(unique_id, model)
        
        self.M   = minat      if minat      is not None else random.uniform(0.3, 1.0)
        self.K   = kemampuan  if kemampuan  is not None else random.uniform(0.3, 1.0)
        self.Sos = sosial     if sosial     is not None else random.uniform(0.1, 0.7)
        self.C   = kebingungan if kebingungan is not None else random.uniform(0.4, 0.9)
        
        self.history_C     = [self.C]
        self.history_score = []
        self.history_state = []
        
        self.state           = 'Bingung'
        self.jurusan_dipilih = None
        self.step_count      = 0
        
        self.active_cbt  = None
        self.cbt_counter = 0
        self.cbt_log     = []

    def hitung_score(self):
        P     = getattr(self.model, 'prospect', 0.6)
        score = (self.M * 0.5) + (self.K * 0.3) + (P * 0.2)
        return round(min(max(score, 0.0), 1.0), 4)

    def update_kebingungan(self):
        S   = getattr(self.model, 'stressor', 0.3)
        I   = getattr(self.model, 'information', 0.5)
        CBT = getattr(self.model, 'cbt', 0.4)
        
        delta = S + (self.Sos * 0.3) - (I * 0.4) - (CBT * 0.5)
        self.C = round(min(max(self.C + delta * 0.15, 0.0), 1.0), 4)

    def ambil_keputusan(self):
        score = self.hitung_score()
        if score >= 0.7 and self.C <= 0.3:
            self.state = 'Yakin'
            if self.jurusan_dipilih is None:
                self.jurusan_dipilih = self._pilih_jurusan()
        elif score >= 0.7 and self.C > 0.3:
            self.state = 'Ragu'
        else:
            self.state = 'Salah'
        return score

    def _pilih_jurusan(self):
        options = ['Teknik Informatika','Psikologi','Kedokteran','Manajemen','Teknik Sipil','Hukum','Ekonomi']
        return random.choice(options)

    def interaksi_sosial(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if not neighbors: return
        
        yakin_neighbors = [a for a in neighbors if a.state == 'Yakin']
        if yakin_neighbors:
            self.C = max(0.0, self.C - 0.02 * len(yakin_neighbors))
            
        salah_neighbors = [a for a in neighbors if a.state == 'Salah']
        if salah_neighbors:
            self.C = min(1.0, self.C + 0.01 * len(salah_neighbors))

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_pos = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_pos)
        
    def apply_cbt(self):
        if   self.C > 0.7:  self.active_cbt = 'konseling_akademik'
        elif self.C > 0.5:  self.active_cbt = 'tes_minat_bakat'
        elif self.C > 0.35: self.active_cbt = 'seminar_jurusan'
        elif self.C > 0.2:  self.active_cbt = 'guru_BK'
        else:               self.active_cbt = 'mentoring'
        
        cbt_multiplier = getattr(self.model, 'cbt', 0.4)
        effect    = self.CBT_TECHNIQUES[self.active_cbt]
        reduction = effect * cbt_multiplier * 0.12
        self.C    = round(max(0.0, self.C - reduction), 4)
        self.cbt_counter += 1
        self.cbt_log.append({'step': self.step_count, 'technique': self.active_cbt,
                             'effect': round(reduction, 4), 'C_after': self.C})

    def step(self):
        self.step_count += 1
        self.move()
        self.interaksi_sosial()
        self.update_kebingungan()
        
        cbt_multiplier = getattr(self.model, 'cbt', 0.4)
        if cbt_multiplier > 0 and self.C > 0.2:
            self.apply_cbt()
            
        score = self.ambil_keputusan()
        self.history_C.append(self.C)
        self.history_score.append(score)
        self.history_state.append(self.state)
