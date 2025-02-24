import React, { useState } from 'react';
import { 
  Container, 
  Grid, 
  TextField, 
  Button, 
  Box,
  Typography
} from '@mui/material';
import axios from 'axios';

interface SceneData {
  sceneName: string;
  sceneGoal: string;
  aiRole: string;
  myRole: string;
  openingLine: string;
  instructions: string;
}

function App() {
  const [userInput, setUserInput] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [sceneData, setSceneData] = useState<SceneData>({
    sceneName: '',
    sceneGoal: '',
    aiRole: '',
    myRole: '',
    openingLine: '',
    instructions: ''
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      const fileType = selectedFile.type;
      if (fileType.includes('pdf') || fileType.includes('image')) {
        setFile(selectedFile);
      } else {
        alert('只支持 PDF 和图片文件');
      }
    }
  };

  const handleOptimize = async () => {
    try {
      const formData = new FormData();
      formData.append('scene_description', userInput);
      if (file) {
        formData.append('file', file);
      }

      const response = await axios.post('http://127.0.0.1:5000/optimize_course_scense', formData);
      
      // 假设后端返回的数据格式与 SceneData 接口匹配
      setSceneData(response.data);
    } catch (error) {
      console.error('优化请求失败:', error);
      alert('优化请求失败');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={4}>
        {/* 左侧部分 */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="请输入文本"
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <Box display="flex" gap={2}>
            <Button
              variant="contained"
              component="label"
            >
              上传附件
              <input
                type="file"
                hidden
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileChange}
              />
            </Button>
            <Button
              variant="contained"
              onClick={handleOptimize}
            >
              AI优化
            </Button>
          </Box>
        </Grid>

        {/* 右侧部分 */}
        <Grid item xs={12} md={6}>
          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              label="场景名称"
              value={sceneData.sceneName}
              onChange={(e) => setSceneData({...sceneData, sceneName: e.target.value})}
              fullWidth
            />
            <TextField
              label="场景目标"
              value={sceneData.sceneGoal}
              onChange={(e) => setSceneData({...sceneData, sceneGoal: e.target.value})}
              fullWidth
            />
            <TextField
              label="AI角色"
              value={sceneData.aiRole}
              onChange={(e) => setSceneData({...sceneData, aiRole: e.target.value})}
              fullWidth
            />
            <TextField
              label="我的角色"
              value={sceneData.myRole}
              onChange={(e) => setSceneData({...sceneData, myRole: e.target.value})}
              fullWidth
            />
            <TextField
              label="开场白"
              value={sceneData.openingLine}
              onChange={(e) => setSceneData({...sceneData, openingLine: e.target.value})}
              fullWidth
            />
            <TextField
              label="要求指令"
              value={sceneData.instructions}
              onChange={(e) => setSceneData({...sceneData, instructions: e.target.value})}
              fullWidth
            />
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
