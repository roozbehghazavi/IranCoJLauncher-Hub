TraceDef()
{
	LifeTime()
	{
		keyf(10, 530)
	}

	Size()
	{
		randf(0, 6,9 )
	}

	MaxNumTraces(120)

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(25, 1, 1, 1, 1)
		keyv4(30, 1, 1, 1, 0)
	}

	Material("CustomWeaponHitTracesBlood.mat")

	TexMultiRect(2, 2, 1, 0)
//	TexPlayMode("pingpong", 20)
}