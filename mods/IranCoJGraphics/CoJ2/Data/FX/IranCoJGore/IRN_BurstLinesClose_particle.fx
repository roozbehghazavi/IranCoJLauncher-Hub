ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GravityMul()
	{
		randf(0, 0.7, 1)
	}

	Drag()
	{
		randf(0, 3, 4)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 1)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.86)
		keyv4(0.27, 0.55, 0.55, 0.55, 0.53)
		keyv4(0.47, 0.55, 0.55, 0.55, 0.25)
		keyv4(1, 0.55, 0.55, 0.55, 0.12)
		keyv4(1.2, 0.55, 0.55, 0.55, 0.1)
		keyv4(1.5, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		randf(0, 45, 55)
	}

	Align("on_start")

	AspectRatio()
	{
		randf(0, 0.1, 0.2)
	}

	Material("IRN_BloodLine_particleBLEND.mat", "IRN_BloodLine_particleBLEND.mat")

	TexMultiRect(4, 1, 4)
	TexPlayMode("random_once", 1)
}
