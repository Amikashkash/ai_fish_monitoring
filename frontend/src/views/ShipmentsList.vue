<template>
  <div class="shipments-page">
    <div class="page-header">
      <h2>Shipments</h2>
      <div class="header-actions" v-if="isAdmin">
        <router-link to="/import" class="btn-primary">Import Invoice</router-link>
        <button class="btn-secondary" @click="openNewInvoiceModal">+ New Shipment</button>
      </div>
    </div>

    <div v-if="loading" class="loading-msg">Loading shipments...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else-if="!invoices.length && !standaloneShipments.length" class="empty-state">
      <p>No shipments yet.</p>
      <router-link to="/import" class="btn-primary">Import your first invoice</router-link>
    </div>

    <div v-else>
      <!-- Invoices accordion list -->
      <div v-if="invoices.length" class="accordion-list">
        <div v-for="inv in invoices" :key="inv.id" class="invoice-card">

          <!-- Clickable header -->
          <div class="invoice-header" @click="toggleInvoice(inv.id)">
            <div class="invoice-summary">
              <span class="chevron" :class="{ open: expandedInvoices[inv.id] }">▶</span>
              <div class="invoice-text">
                <span class="invoice-date">{{ inv.date }}</span>
                <span v-if="inv.supplier_name" class="invoice-supplier"> — {{ inv.supplier_name }}</span>
                <span v-if="inv.invoice_number" class="invoice-num"> #{{ inv.invoice_number }}</span>
              </div>
            </div>
            <div class="invoice-badges">
              <span v-if="inv.source" class="badge-source">{{ inv.source }}</span>
              <span class="badge-count">{{ (inv.shipments || []).length }} species</span>
            </div>
          </div>

          <!-- Expanded body -->
          <div v-if="expandedInvoices[inv.id]" class="invoice-body">
            <div v-if="!(inv.shipments || []).length" class="no-fish">
              No fish added yet. Click "+ Add Fish" to start.
            </div>

            <div v-for="fish in (inv.shipments || [])" :key="fish.id" class="fish-row">
              <div class="fish-info">
                <span class="fish-sci">{{ fish.scientific_name }}</span>
                <span v-if="fish.common_name && fish.common_name !== fish.scientific_name" class="fish-common"> ({{ fish.common_name }})</span>
                <span class="fish-qty"> — {{ fish.quantity }} fish</span>
                <span v-if="fish.aquarium_number" class="fish-tank"> | {{ fish.aquarium_number }}</span>
                <span v-if="fish.aquarium_volume_liters && fish.aquarium_volume_liters > 1" class="fish-vol"> {{ fish.aquarium_volume_liters }}L</span>
                <span v-if="fish.fish_size" class="fish-size-badge"> {{ fish.fish_size }}</span>
              </div>
              <div class="fish-actions" v-if="isAdmin">
                <button class="btn-treat-sm" @click.stop="openTreatModal(fish)">Treat</button>
                <button class="btn-edit-sm" @click.stop="openEditModal(fish)">Edit</button>
                <button class="btn-del-sm" @click.stop="confirmDelete(fish)">Del</button>
              </div>
            </div>

            <div class="invoice-footer" v-if="isAdmin">
              <button class="btn-add-fish" @click.stop="openAddFishModal(inv)">+ Add Fish</button>
              <button class="btn-edit-inv" @click.stop="openEditInvoiceModal(inv)">Edit Invoice</button>
              <button class="btn-del-inv" @click.stop="confirmDeleteInvoice(inv)">Delete Invoice</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Standalone fish (no invoice) -->
      <div v-if="standaloneShipments.length">
        <div v-if="invoices.length" class="section-label">Standalone Fish</div>
        <div class="shipments-grid">
          <div v-for="s in standaloneShipments" :key="s.id" class="shipment-card">
            <div class="card-top">
              <div class="card-title">
                <p class="sci-name">{{ s.scientific_name }}</p>
                <p class="common-name">{{ s.common_name && s.common_name !== s.scientific_name ? s.common_name : '' }}</p>
              </div>
              <div class="card-badges">
                <span class="aquarium-badge" v-if="s.aquarium_number">{{ s.aquarium_number }}</span>
                <span class="status-badge no-tank" v-else>No tank assigned</span>
              </div>
            </div>

            <div class="card-details">
              <div class="detail">
                <span class="detail-label">Source</span>
                <span>{{ s.source }}</span>
              </div>
              <div class="detail">
                <span class="detail-label">Quantity</span>
                <span>{{ s.quantity }} fish</span>
              </div>
              <div class="detail">
                <span class="detail-label">Arrived</span>
                <span>{{ s.date }}</span>
              </div>
              <div class="detail" v-if="s.aquarium_volume_liters && s.aquarium_volume_liters > 1">
                <span class="detail-label">Tank Vol</span>
                <span>{{ s.aquarium_volume_liters }}L</span>
              </div>
              <div class="detail" v-if="s.fish_size">
                <span class="detail-label">Size</span>
                <span>{{ s.fish_size }}</span>
              </div>
              <div class="detail" v-if="s.supplier_name">
                <span class="detail-label">Supplier</span>
                <span>{{ s.supplier_name }}</span>
              </div>
              <div class="detail" v-if="s.invoice_number">
                <span class="detail-label">Invoice</span>
                <span>{{ s.invoice_number }}</span>
              </div>
            </div>

            <div class="card-actions" v-if="isAdmin">
              <button class="btn-treat" @click="openTreatModal(s)">Start Treatment</button>
              <button class="btn-edit" @click="openEditModal(s)" title="Edit">Edit</button>
              <button class="btn-delete" @click="confirmDelete(s)" title="Delete">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ NEW INVOICE MODAL ══ -->
    <div v-if="showNewInvoiceModal" class="modal-backdrop" @click.self="showNewInvoiceModal = false">
      <div class="modal modal-wide">
        <h3>New Shipment</h3>
        <div class="treat-form">
          <div class="form-section">
            <div class="form-row">
              <div class="form-group">
                <label>Arrival Date</label>
                <input v-model="newInvoiceForm.date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Source Country</label>
                <input v-model="newInvoiceForm.source" class="form-input" placeholder="e.g. Thailand" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Supplier Name</label>
                <input v-model="newInvoiceForm.supplier_name" class="form-input" placeholder="e.g. Aqua Fish Ltd" />
              </div>
              <div class="form-group">
                <label>Invoice Number</label>
                <input v-model="newInvoiceForm.invoice_number" class="form-input" placeholder="INV-001" />
              </div>
            </div>
            <div class="form-group">
              <label>Notes</label>
              <input v-model="newInvoiceForm.notes" class="form-input" placeholder="Optional notes" />
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doCreateInvoice" :disabled="creatingInvoice">
            {{ creatingInvoice ? 'Creating...' : 'Create Shipment' }}
          </button>
          <button class="btn-cancel" @click="showNewInvoiceModal = false">Cancel</button>
        </div>
        <p v-if="newInvoiceError" class="error-msg">{{ newInvoiceError }}</p>
      </div>
    </div>

    <!-- ══ ADD FISH MODAL ══ -->
    <div v-if="addFishTarget" class="modal-backdrop" @click.self="addFishTarget = null">
      <div class="modal modal-wide">
        <h3>Add Fish to Invoice</h3>
        <p class="modal-fish">{{ addFishTarget.date }}<span v-if="addFishTarget.supplier_name"> — {{ addFishTarget.supplier_name }}</span></p>
        <div class="treat-form">
          <div class="form-section">
            <div class="form-row">
              <div class="form-group">
                <label>Scientific Name *</label>
                <input v-model="addFishForm.scientific_name" class="form-input" placeholder="e.g. Betta splendens" />
              </div>
              <div class="form-group">
                <label>Common Name</label>
                <input v-model="addFishForm.common_name" class="form-input" placeholder="e.g. Betta" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Quantity *</label>
                <input v-model.number="addFishForm.quantity" type="number" min="1" class="form-input" placeholder="e.g. 50" />
              </div>
              <div class="form-group">
                <label>Fish Size</label>
                <input v-model="addFishForm.fish_size" class="form-input" placeholder="e.g. 3-5cm" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Aquarium / Tank #</label>
                <input v-model="addFishForm.aquarium_number" class="form-input" placeholder="e.g. Tank 3" />
              </div>
              <div class="form-group">
                <label>Tank Volume (Liters)</label>
                <input v-model.number="addFishForm.aquarium_volume_liters" type="number" min="1" class="form-input" placeholder="e.g. 200" />
              </div>
            </div>
            <div class="form-group">
              <label>Price per Fish</label>
              <input v-model.number="addFishForm.price_per_fish" type="number" step="0.01" min="0" class="form-input" placeholder="0.00" />
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doAddFish"
            :disabled="addingFish || !addFishForm.scientific_name || !addFishForm.quantity">
            {{ addingFish ? 'Adding...' : 'Add Fish' }}
          </button>
          <button class="btn-cancel" @click="addFishTarget = null">Cancel</button>
        </div>
        <p v-if="addFishError" class="error-msg">{{ addFishError }}</p>
      </div>
    </div>

    <!-- ══ EDIT INVOICE MODAL ══ -->
    <div v-if="editInvoiceTarget" class="modal-backdrop" @click.self="editInvoiceTarget = null">
      <div class="modal modal-wide">
        <h3>Edit Invoice</h3>
        <div class="treat-form">
          <div class="form-section">
            <div class="form-row">
              <div class="form-group">
                <label>Arrival Date</label>
                <input v-model="editInvoiceForm.date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Source Country</label>
                <input v-model="editInvoiceForm.source" class="form-input" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Supplier Name</label>
                <input v-model="editInvoiceForm.supplier_name" class="form-input" />
              </div>
              <div class="form-group">
                <label>Invoice Number</label>
                <input v-model="editInvoiceForm.invoice_number" class="form-input" />
              </div>
            </div>
            <div class="form-group">
              <label>Notes</label>
              <input v-model="editInvoiceForm.notes" class="form-input" />
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doEditInvoice" :disabled="editingInvoice">
            {{ editingInvoice ? 'Saving...' : 'Save Changes' }}
          </button>
          <button class="btn-cancel" @click="editInvoiceTarget = null">Cancel</button>
        </div>
        <p v-if="editInvoiceError" class="error-msg">{{ editInvoiceError }}</p>
      </div>
    </div>

    <!-- ══ DELETE INVOICE CONFIRMATION ══ -->
    <div v-if="deleteInvoiceTarget" class="modal-backdrop" @click.self="deleteInvoiceTarget = null">
      <div class="modal">
        <h3>Delete Invoice?</h3>
        <p class="modal-fish">
          {{ deleteInvoiceTarget.date }}
          <span v-if="deleteInvoiceTarget.supplier_name"> — {{ deleteInvoiceTarget.supplier_name }}</span>
        </p>
        <p class="modal-warn">
          The invoice will be deleted. Fish inside will become standalone (not deleted).
          Treatments are not affected.
        </p>
        <div class="modal-actions">
          <button class="btn-delete-confirm" @click="doDeleteInvoice" :disabled="deletingInvoice">
            {{ deletingInvoice ? 'Deleting...' : 'Yes, Delete Invoice' }}
          </button>
          <button class="btn-cancel" @click="deleteInvoiceTarget = null">Cancel</button>
        </div>
        <p v-if="deleteInvoiceError" class="error-msg">{{ deleteInvoiceError }}</p>
      </div>
    </div>

    <!-- ══ DELETE FISH CONFIRMATION ══ -->
    <div v-if="deleteTarget" class="modal-backdrop" @click.self="deleteTarget = null">
      <div class="modal">
        <h3>Delete Fish?</h3>
        <p class="modal-fish">
          <span v-if="deleteTarget.common_name && deleteTarget.common_name !== deleteTarget.scientific_name">
            {{ deleteTarget.common_name }} —
          </span>
          <em>{{ deleteTarget.scientific_name }}</em> — {{ deleteTarget.quantity }} fish
        </p>
        <p class="modal-warn">This cannot be undone. Use this for DOA, shipping problems, or data entry errors.</p>
        <div class="modal-reason">
          <label>Reason (optional)</label>
          <select v-model="deleteReason">
            <option value="">Select reason...</option>
            <option value="DOA">DOA – Dead on Arrival</option>
            <option value="Refused">Refused – poor condition</option>
            <option value="Wrong species">Wrong species received</option>
            <option value="Entry error">Data entry error</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-delete-confirm" @click="doDelete" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Yes, Delete' }}
          </button>
          <button class="btn-cancel" @click="deleteTarget = null">Cancel</button>
        </div>
        <p v-if="deleteError" class="error-msg">{{ deleteError }}</p>
      </div>
    </div>

    <!-- ══ START TREATMENT MODAL ══ -->
    <div v-if="treatTarget" class="modal-backdrop" @click.self="closeTreatModal">
      <div class="modal modal-wide">
        <h3>Start Treatment</h3>
        <p class="modal-fish">
          <span v-if="treatTarget.common_name && treatTarget.common_name !== treatTarget.scientific_name">
            {{ treatTarget.common_name }} —
          </span>
          <em>{{ treatTarget.scientific_name }}</em> — {{ treatTarget.quantity }} fish
        </p>

        <div class="treat-form">
          <div class="form-section">
            <h4>Aquarium Assignment</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Aquarium / Tank # *</label>
                <input v-model="treatForm.aquarium_number" placeholder="e.g. Tank 3, QT-1" class="form-input" />
              </div>
              <div class="form-group">
                <label>Tank Volume (Liters) *</label>
                <input v-model.number="treatForm.aquarium_volume_liters" type="number" min="1" placeholder="e.g. 200" class="form-input" />
              </div>
            </div>
            <p class="density-hint" v-if="treatForm.aquarium_volume_liters > 0">
              Density: {{ (treatTarget.quantity / treatForm.aquarium_volume_liters).toFixed(2) }} fish/L
            </p>
          </div>

          <div class="form-section">
            <h4>Treatment Drugs <span class="optional-label">(optional – add later)</span></h4>
            <div v-if="protocols.length" class="drug-list">
              <label v-for="p in protocols" :key="p.id" class="drug-checkbox">
                <input type="checkbox" :value="p.id" v-model="selectedProtocols" />
                <span class="drug-name">{{ p.drug_name }}</span>
                <span class="drug-info" v-if="p.standard_dosage">{{ p.standard_dosage }} {{ p.dosage_unit }}</span>
              </label>
            </div>
            <p v-else class="no-drugs">No drug protocols defined yet.</p>
          </div>

          <div class="form-section">
            <div class="form-group">
              <label>Treatment Start Date</label>
              <input v-model="treatForm.start_date" type="date" class="form-input" />
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doStartTreatment"
            :disabled="treating || !treatForm.aquarium_number || !treatForm.aquarium_volume_liters">
            {{ treating ? 'Starting...' : 'Start Treatment' }}
          </button>
          <button class="btn-cancel" @click="closeTreatModal">Cancel</button>
        </div>
        <p v-if="treatError" class="error-msg">{{ treatError }}</p>
      </div>
    </div>

    <!-- ══ EDIT FISH MODAL ══ -->
    <div v-if="editTarget" class="modal-backdrop" @click.self="editTarget = null">
      <div class="modal modal-wide">
        <h3>Edit Fish</h3>
        <p class="modal-fish"><em>{{ editTarget.scientific_name }}</em></p>
        <div class="treat-form">
          <div class="form-section">
            <div class="form-row">
              <div class="form-group">
                <label>Tank / Aquarium #</label>
                <input v-model="editForm.aquarium_number" type="text" class="form-input" placeholder="e.g. Tank 3, QT-1" />
              </div>
              <div class="form-group">
                <label>Tank Volume (Liters)</label>
                <input v-model.number="editForm.aquarium_volume_liters" type="number" min="1" class="form-input" placeholder="e.g. 200" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Common Name</label>
                <input v-model="editForm.common_name" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Fish Size</label>
                <input v-model="editForm.fish_size" type="text" class="form-input" placeholder="e.g. 3-5cm" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Supplier</label>
                <input v-model="editForm.supplier_name" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Notes</label>
                <input v-model="editForm.notes" type="text" class="form-input" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-treat-confirm" @click="doEdit" :disabled="editing">
            {{ editing ? 'Saving...' : 'Save Changes' }}
          </button>
          <button class="btn-cancel" @click="editTarget = null">Cancel</button>
        </div>
        <p v-if="editError" class="error-msg">{{ editError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { invoicesAPI, shipmentsAPI, treatmentsAPI, protocolsAPI } from "../api/client.js";
import { useAuth } from "../composables/useAuth.js";

export default {
  name: "ShipmentsList",
  setup() {
    const { isAdmin } = useAuth();
    return { isAdmin };
  },
  data() {
    return {
      invoices: [],
      standaloneShipments: [],
      expandedInvoices: {},
      loading: true,
      error: "",
      // New Invoice
      showNewInvoiceModal: false,
      newInvoiceForm: { date: new Date().toISOString().split("T")[0], source: "", supplier_name: "", invoice_number: "", notes: "" },
      creatingInvoice: false,
      newInvoiceError: "",
      // Add Fish
      addFishTarget: null,
      addFishForm: { scientific_name: "", common_name: "", quantity: null, fish_size: "", aquarium_number: "", aquarium_volume_liters: null, price_per_fish: null },
      addingFish: false,
      addFishError: "",
      // Edit Invoice
      editInvoiceTarget: null,
      editInvoiceForm: {},
      editingInvoice: false,
      editInvoiceError: "",
      // Delete Invoice
      deleteInvoiceTarget: null,
      deletingInvoice: false,
      deleteInvoiceError: "",
      // Delete Fish
      deleteTarget: null,
      deleteReason: "",
      deleting: false,
      deleteError: "",
      // Start Treatment
      treatTarget: null,
      protocols: [],
      selectedProtocols: [],
      treatForm: { aquarium_number: "", aquarium_volume_liters: null, start_date: new Date().toISOString().split("T")[0] },
      treating: false,
      treatError: "",
      // Edit Fish
      editTarget: null,
      editForm: {},
      editing: false,
      editError: ""
    };
  },
  mounted() {
    this.load();
    this.loadProtocols();
  },
  methods: {
    async load() {
      this.loading = true;
      this.error = "";
      try {
        // Load invoices with nested fish
        let invoiceData = [];
        try {
          const invRes = await invoicesAPI.list();
          invoiceData = invRes.data || [];
        } catch {
          // invoices table may not exist yet (migration pending)
          invoiceData = [];
        }
        this.invoices = invoiceData;

        // Load all shipments, filter out those already inside an invoice
        const shipRes = await shipmentsAPI.list({ limit: 200 });
        const allShipments = shipRes.data.shipments || [];
        const invoiceShipmentIds = new Set(
          invoiceData.flatMap(inv => (inv.shipments || []).map(f => f.id))
        );
        this.standaloneShipments = allShipments.filter(s => !invoiceShipmentIds.has(s.id));
      } catch (e) {
        this.error = e.response?.data?.detail || "Failed to load shipments.";
      } finally {
        this.loading = false;
      }
    },
    async loadProtocols() {
      try {
        const res = await protocolsAPI.list();
        this.protocols = res.data;
      } catch {
        // silent
      }
    },
    toggleInvoice(id) {
      this.expandedInvoices = { ...this.expandedInvoices, [id]: !this.expandedInvoices[id] };
    },

    // ── New Invoice ──
    openNewInvoiceModal() {
      this.newInvoiceForm = { date: new Date().toISOString().split("T")[0], source: "", supplier_name: "", invoice_number: "", notes: "" };
      this.newInvoiceError = "";
      this.showNewInvoiceModal = true;
    },
    async doCreateInvoice() {
      this.creatingInvoice = true;
      this.newInvoiceError = "";
      try {
        const res = await invoicesAPI.create(this.newInvoiceForm);
        const newInvoice = { ...res.data, shipments: [] };
        this.invoices.unshift(newInvoice);
        this.expandedInvoices = { ...this.expandedInvoices, [newInvoice.id]: true };
        this.showNewInvoiceModal = false;
      } catch (e) {
        this.newInvoiceError = e.response?.data?.detail || "Failed to create invoice.";
      } finally {
        this.creatingInvoice = false;
      }
    },

    // ── Add Fish ──
    openAddFishModal(inv) {
      this.addFishTarget = inv;
      this.addFishForm = { scientific_name: "", common_name: "", quantity: null, fish_size: "", aquarium_number: "", aquarium_volume_liters: null, price_per_fish: null };
      this.addFishError = "";
    },
    async doAddFish() {
      this.addingFish = true;
      this.addFishError = "";
      try {
        const res = await invoicesAPI.addFish(this.addFishTarget.id, this.addFishForm);
        const newFish = res.data;
        const inv = this.invoices.find(i => i.id === this.addFishTarget.id);
        if (inv) {
          inv.shipments = [...(inv.shipments || []), newFish];
        }
        this.addFishTarget = null;
      } catch (e) {
        this.addFishError = e.response?.data?.detail || "Failed to add fish.";
      } finally {
        this.addingFish = false;
      }
    },

    // ── Edit Invoice ──
    openEditInvoiceModal(inv) {
      this.editInvoiceTarget = inv;
      this.editInvoiceForm = {
        date: inv.date || "",
        source: inv.source || "",
        supplier_name: inv.supplier_name || "",
        invoice_number: inv.invoice_number || "",
        notes: inv.notes || ""
      };
      this.editInvoiceError = "";
    },
    async doEditInvoice() {
      this.editingInvoice = true;
      this.editInvoiceError = "";
      try {
        await invoicesAPI.update(this.editInvoiceTarget.id, this.editInvoiceForm);
        const inv = this.invoices.find(i => i.id === this.editInvoiceTarget.id);
        if (inv) Object.assign(inv, this.editInvoiceForm);
        this.editInvoiceTarget = null;
      } catch (e) {
        this.editInvoiceError = e.response?.data?.detail || "Failed to update invoice.";
      } finally {
        this.editingInvoice = false;
      }
    },

    // ── Delete Invoice ──
    confirmDeleteInvoice(inv) {
      this.deleteInvoiceTarget = inv;
      this.deleteInvoiceError = "";
    },
    async doDeleteInvoice() {
      this.deletingInvoice = true;
      this.deleteInvoiceError = "";
      try {
        await invoicesAPI.delete(this.deleteInvoiceTarget.id);
        // Fish become standalone — move them
        const freed = (this.deleteInvoiceTarget.shipments || []);
        this.standaloneShipments = [...freed, ...this.standaloneShipments];
        this.invoices = this.invoices.filter(i => i.id !== this.deleteInvoiceTarget.id);
        this.deleteInvoiceTarget = null;
      } catch (e) {
        this.deleteInvoiceError = e.response?.data?.detail || "Failed to delete invoice.";
      } finally {
        this.deletingInvoice = false;
      }
    },

    // ── Delete Fish ──
    confirmDelete(fish) {
      this.deleteTarget = fish;
      this.deleteReason = "";
      this.deleteError = "";
    },
    async doDelete() {
      this.deleting = true;
      this.deleteError = "";
      try {
        await shipmentsAPI.delete(this.deleteTarget.id);
        const id = this.deleteTarget.id;
        // Remove from invoice
        this.invoices.forEach(inv => {
          inv.shipments = (inv.shipments || []).filter(f => f.id !== id);
        });
        // Remove from standalone
        this.standaloneShipments = this.standaloneShipments.filter(s => s.id !== id);
        this.deleteTarget = null;
      } catch (e) {
        this.deleteError = e.response?.data?.detail || "Failed to delete.";
      } finally {
        this.deleting = false;
      }
    },

    // ── Start Treatment ──
    openTreatModal(fish) {
      this.treatTarget = fish;
      this.treatError = "";
      this.selectedProtocols = [];
      this.treatForm = {
        aquarium_number: fish.aquarium_number || "",
        aquarium_volume_liters: fish.aquarium_volume_liters > 1 ? fish.aquarium_volume_liters : null,
        start_date: new Date().toISOString().split("T")[0]
      };
    },
    closeTreatModal() {
      this.treatTarget = null;
      this.treatError = "";
    },
    async doStartTreatment() {
      if (!this.treatForm.aquarium_number || !this.treatForm.aquarium_volume_liters) return;
      this.treating = true;
      this.treatError = "";
      try {
        await shipmentsAPI.update(this.treatTarget.id, {
          aquarium_number: this.treatForm.aquarium_number,
          aquarium_volume_liters: this.treatForm.aquarium_volume_liters
        });
        const drugs = this.selectedProtocols.map(id => ({ drug_protocol_id: id }));
        await treatmentsAPI.create({
          shipment_id: this.treatTarget.id,
          start_date: this.treatForm.start_date,
          drugs
        });
        this.closeTreatModal();
        this.$router.push("/treatments");
      } catch (e) {
        const detail = e.response?.data?.detail;
        this.treatError = typeof detail === "string" ? detail : (e.message || "Failed to start treatment.");
      } finally {
        this.treating = false;
      }
    },

    // ── Edit Fish ──
    openEditModal(fish) {
      this.editTarget = fish;
      this.editError = "";
      this.editForm = {
        aquarium_number: fish.aquarium_number || "",
        aquarium_volume_liters: fish.aquarium_volume_liters > 1 ? fish.aquarium_volume_liters : null,
        common_name: fish.common_name || "",
        fish_size: fish.fish_size || "",
        supplier_name: fish.supplier_name || "",
        notes: fish.notes || ""
      };
    },
    async doEdit() {
      this.editing = true;
      this.editError = "";
      try {
        const patch = {};
        for (const [k, v] of Object.entries(this.editForm)) {
          if (v !== "" && v != null) patch[k] = v;
        }
        await shipmentsAPI.update(this.editTarget.id, patch);
        // Update in invoices
        this.invoices.forEach(inv => {
          const fish = (inv.shipments || []).find(f => f.id === this.editTarget.id);
          if (fish) Object.assign(fish, patch);
        });
        // Update in standalone
        const s = this.standaloneShipments.find(s => s.id === this.editTarget.id);
        if (s) Object.assign(s, patch);
        this.editTarget = null;
      } catch (e) {
        this.editError = e.response?.data?.detail || "Failed to save changes.";
      } finally {
        this.editing = false;
      }
    }
  }
};
</script>

<style scoped>
.shipments-page { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h2 { font-size: 1.5rem; color: #1e293b; margin: 0; }
.header-actions { display: flex; gap: 0.5rem; }

.loading-msg { text-align: center; color: #64748b; padding: 2rem; }
.error-msg { color: #dc2626; margin-top: 0.5rem; font-size: 0.9rem; }
.empty-state { text-align: center; padding: 3rem; color: #64748b; }
.empty-state p { margin-bottom: 1rem; font-size: 1.1rem; }

/* Accordion */
.accordion-list { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 2rem; }
.invoice-card { background: white; border-radius: 0.75rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); overflow: hidden; }

.invoice-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.25rem; cursor: pointer; user-select: none;
  transition: background 0.15s;
}
.invoice-header:hover { background: #f8fafc; }

.invoice-summary { display: flex; align-items: center; gap: 0.75rem; }
.chevron { display: inline-block; transition: transform 0.2s; font-size: 0.75rem; color: #94a3b8; }
.chevron.open { transform: rotate(90deg); }

.invoice-text { font-size: 0.95rem; }
.invoice-date { font-weight: 700; color: #1e293b; }
.invoice-supplier { color: #374151; }
.invoice-num { color: #64748b; font-size: 0.85rem; }

.invoice-badges { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.badge-source { background: #e0f2fe; color: #0369a1; font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.55rem; border-radius: 1rem; }
.badge-count { background: #f1f5f9; color: #64748b; font-size: 0.75rem; padding: 0.2rem 0.55rem; border-radius: 1rem; }

.invoice-body { border-top: 1px solid #f1f5f9; padding: 0.75rem 1.25rem; }
.no-fish { color: #94a3b8; font-size: 0.9rem; padding: 0.5rem 0; }

.fish-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.5rem 0; border-bottom: 1px solid #f8fafc;
}
.fish-row:last-of-type { border-bottom: none; }
.fish-info { font-size: 0.875rem; flex: 1; }
.fish-sci { font-style: italic; font-weight: 600; color: #1e293b; }
.fish-common { color: #64748b; }
.fish-qty { color: #374151; }
.fish-tank { color: #0284c7; font-weight: 600; }
.fish-vol { color: #64748b; font-size: 0.8rem; }
.fish-size-badge { color: #94a3b8; font-size: 0.8rem; }

.fish-actions { display: flex; gap: 0.35rem; flex-shrink: 0; }
.btn-treat-sm { background: #0ea5e9; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 0.35rem; cursor: pointer; font-size: 0.78rem; font-weight: 600; }
.btn-treat-sm:hover { background: #0284c7; }
.btn-edit-sm { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 0.3rem 0.6rem; border-radius: 0.35rem; cursor: pointer; font-size: 0.78rem; }
.btn-edit-sm:hover { background: #dcfce7; }
.btn-del-sm { background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 0.3rem 0.6rem; border-radius: 0.35rem; cursor: pointer; font-size: 0.78rem; }
.btn-del-sm:hover { background: #ffe4e6; }

.invoice-footer {
  display: flex; gap: 0.5rem; padding-top: 0.75rem; margin-top: 0.25rem;
  border-top: 1px dashed #e2e8f0;
}
.btn-add-fish { background: #f0f9ff; color: #0284c7; border: 1px solid #bae6fd; padding: 0.4rem 0.85rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; font-weight: 600; }
.btn-add-fish:hover { background: #e0f2fe; }
.btn-edit-inv { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 0.4rem 0.85rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; }
.btn-edit-inv:hover { background: #dcfce7; }
.btn-del-inv { background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 0.4rem 0.85rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; }
.btn-del-inv:hover { background: #ffe4e6; }

/* Section label */
.section-label { font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }

/* Standalone grid (legacy) */
.shipments-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.shipment-card { background: white; border-radius: 0.75rem; padding: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 0.75rem; }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.sci-name { font-weight: 700; color: #1e293b; font-style: italic; margin: 0; }
.common-name { color: #64748b; font-size: 0.85rem; margin: 0.2rem 0 0; }
.card-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; flex-shrink: 0; }
.aquarium-badge { background: #0ea5e9; color: white; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 1rem; }
.status-badge.no-tank { background: #f1f5f9; color: #94a3b8; font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 1rem; }
.card-details { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; }
.detail { display: flex; flex-direction: column; }
.detail-label { font-size: 0.7rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
.detail span:last-child { font-size: 0.85rem; color: #374151; }
.card-actions { display: flex; gap: 0.5rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem; }
.btn-treat { flex: 1; background: #0ea5e9; color: white; border: none; padding: 0.45rem 0.75rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; font-weight: 600; }
.btn-treat:hover { background: #0284c7; }
.btn-edit { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 0.45rem 0.75rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; }
.btn-edit:hover { background: #dcfce7; }
.btn-delete { background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 0.45rem 0.75rem; border-radius: 0.4rem; cursor: pointer; font-size: 0.85rem; }
.btn-delete:hover { background: #ffe4e6; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem; }
.modal { background: white; border-radius: 0.75rem; padding: 1.75rem; width: 100%; max-width: 420px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-height: 90vh; overflow-y: auto; }
.modal-wide { max-width: 580px; }
.modal h3 { font-size: 1.2rem; color: #1e293b; margin: 0 0 0.5rem; }
.modal-fish { font-weight: 600; color: #0284c7; margin: 0 0 0.75rem; font-size: 0.95rem; }
.modal-warn { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
.modal-reason { margin-bottom: 1.25rem; }
.modal-reason label { display: block; font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 0.35rem; }
.modal-reason select { width: 100%; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 0.4rem; font-size: 0.9rem; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; }
.btn-delete-confirm { flex: 1; background: #e11d48; color: white; border: none; padding: 0.6rem 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: 600; }
.btn-delete-confirm:hover { background: #be123c; }
.btn-delete-confirm:disabled { opacity: 0.6; cursor: default; }
.btn-cancel { flex: 1; background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 0.6rem 1rem; border-radius: 0.5rem; cursor: pointer; }

.treat-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-section { background: #f8fafc; border-radius: 0.5rem; padding: 1rem; }
.form-section h4 { font-size: 0.9rem; color: #1e293b; margin: 0 0 0.75rem; font-weight: 700; }
.optional-label { color: #94a3b8; font-weight: 400; font-size: 0.8rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.form-group label { font-size: 0.8rem; font-weight: 600; color: #64748b; }
.form-input { border: 1px solid #e2e8f0; border-radius: 0.4rem; padding: 0.5rem 0.65rem; font-size: 0.9rem; outline: none; width: 100%; box-sizing: border-box; }
.form-input:focus { border-color: #0ea5e9; }
.density-hint { margin-top: 0.5rem; font-size: 0.8rem; color: #0284c7; font-weight: 600; }

.drug-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 180px; overflow-y: auto; }
.drug-checkbox { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; padding: 0.35rem 0.5rem; border-radius: 0.35rem; }
.drug-checkbox:hover { background: #e0f2fe; }
.drug-name { font-size: 0.9rem; font-weight: 500; color: #1e293b; flex: 1; }
.drug-info { font-size: 0.8rem; color: #64748b; }
.no-drugs { font-size: 0.85rem; color: #94a3b8; }

.btn-treat-confirm { flex: 1; background: #0ea5e9; color: white; border: none; padding: 0.65rem 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: 600; font-size: 0.95rem; }
.btn-treat-confirm:hover { background: #0284c7; }
.btn-treat-confirm:disabled { opacity: 0.5; cursor: default; }

.btn-primary { background: #0ea5e9; color: white; border: none; padding: 0.55rem 1.1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.9rem; font-weight: 600; text-decoration: none; display: inline-block; }
.btn-primary:hover { background: #0284c7; }
.btn-secondary { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 0.55rem 1.1rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.9rem; text-decoration: none; display: inline-block; }
.btn-secondary:hover { background: #e2e8f0; }
</style>
