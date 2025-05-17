// scanSlice.js
import { createSlice } from '@reduxjs/toolkit'

const initialState = { result: null }

const scanSlice = createSlice({
  name: 'scan',
  initialState,
  reducers: {
    setResult: (state, action) => {
      state.result = action.payload
    }
  }
})

export const { setResult } = scanSlice.actions
export default scanSlice.reducer
